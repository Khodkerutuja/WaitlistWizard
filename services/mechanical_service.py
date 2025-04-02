from datetime import datetime
from models.mechanical import MechanicalService as MechanicalServiceModel, MechanicalServiceType
from models.enum_types import BookingStatus
from repositories.mechanical_repository import MechanicalRepository
from repositories.booking_repository import BookingRepository
from services.wallet_service import WalletService
from app import db

class MechanicalService:
    def __init__(self):
        self.mechanical_repository = MechanicalRepository()
        self.booking_repository = BookingRepository()
        self.wallet_service = WalletService()
    
    def get_mechanical_services(self, mechanical_type=None, offers_pickup=None, location=None):
        """
        Get mechanical services, optionally filtered
        
        Args:
            mechanical_type: Filter by mechanical service type (optional)
            offers_pickup: Filter by pickup service availability (optional)
            location: Filter by location (optional)
            
        Returns:
            List of mechanical service objects
        """
        return self.mechanical_repository.find_all(
            mechanical_type=mechanical_type,
            offers_pickup=offers_pickup,
            location=location
        )
    
    def create_mechanical_service(self, name, description, provider_id, mechanical_type, service_charge,
                                additional_charges_desc=None, estimated_time=None, offers_pickup=False,
                                pickup_charge=None, location=None, availability=None):
        """
        Create a new mechanical service
        
        Args:
            name: Service name
            description: Service description
            provider_id: ID of the service provider
            mechanical_type: Type of mechanical service
            service_charge: Fixed service charge
            additional_charges_desc: Description of additional charges (optional)
            estimated_time: Estimated time in minutes (optional)
            offers_pickup: Whether pickup service is offered (optional)
            pickup_charge: Charge for pickup service (optional)
            location: Service location (optional)
            availability: Service availability (optional)
            
        Returns:
            Newly created mechanical service object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate mechanical type
        if mechanical_type not in [MechanicalServiceType.BIKE_REPAIR, MechanicalServiceType.CAR_REPAIR, 
                                  MechanicalServiceType.GENERAL_MAINTENANCE, MechanicalServiceType.BREAKDOWN_ASSISTANCE, 
                                  MechanicalServiceType.TOWING, MechanicalServiceType.OTHER]:
            raise ValueError(f"Invalid mechanical service type: {mechanical_type}")
        
        # Validate service charge
        if not service_charge or service_charge <= 0:
            raise ValueError("Service charge must be positive")
        
        # Validate pickup charge if pickup offered
        if offers_pickup and pickup_charge is None:
            raise ValueError("Pickup charge must be provided if pickup service is offered")
        
        # Create mechanical service
        service = MechanicalServiceModel(
            name=name,
            description=description,
            provider_id=provider_id,
            service_charge=service_charge,
            mechanical_type=mechanical_type,
            additional_charges_desc=additional_charges_desc,
            estimated_time=estimated_time,
            offers_pickup=offers_pickup,
            pickup_charge=pickup_charge,
            location=location,
            availability=availability
        )
        
        # Save service
        return self.mechanical_repository.create(service)
    
    def update_mechanical_service(self, service_id, provider_id, data):
        """
        Update a mechanical service
        
        Args:
            service_id: ID of the service to update
            provider_id: ID of the service provider (for authorization)
            data: Dictionary of fields to update
            
        Returns:
            Updated mechanical service object
            
        Raises:
            ValueError: If service not found or provider not authorized
        """
        # Get service
        service = self.mechanical_repository.find_by_id(service_id)
        if not service:
            raise ValueError(f"Mechanical service with ID {service_id} not found")
        
        # Check if provider is authorized
        if service.provider_id != provider_id:
            raise ValueError("Not authorized to update this service")
        
        # Update base service fields
        if 'name' in data:
            service.name = data['name']
        if 'description' in data:
            service.description = data['description']
        
        # Update mechanical service specific fields
        if 'service_charge' in data:
            service.service_charge = data['service_charge']
            service.price = data['service_charge']  # Update base price as well
        if 'additional_charges_desc' in data:
            service.additional_charges_desc = data['additional_charges_desc']
        if 'estimated_time' in data:
            service.estimated_time = data['estimated_time']
        if 'offers_pickup' in data:
            service.offers_pickup = data['offers_pickup']
        if 'pickup_charge' in data:
            service.pickup_charge = data['pickup_charge']
        if 'location' in data:
            service.location = data['location']
        if 'availability' in data:
            service.availability = data['availability']
        
        # Save updated service
        return self.mechanical_repository.update(service)
    
    def book_mechanical_service(self, user_id, service_id, booking_time, vehicle_details=None,
                              issue_description=None, pickup_required=False, pickup_address=None):
        """
        Book a mechanical service
        
        Args:
            user_id: ID of the user booking the service
            service_id: ID of the service to book
            booking_time: Date and time of the booking
            vehicle_details: Details of the vehicle (optional)
            issue_description: Description of the issue (optional)
            pickup_required: Whether pickup is required (optional)
            pickup_address: Pickup address (optional)
            
        Returns:
            Newly created booking object
            
        Raises:
            ValueError: If service not found, invalid booking details, or other validation fails
        """
        # Get service
        service = self.mechanical_repository.find_by_id(service_id)
        if not service:
            raise ValueError(f"Mechanical service with ID {service_id} not found")
        
        # Parse booking time
        if isinstance(booking_time, str):
            try:
                booking_time = datetime.fromisoformat(booking_time.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("Invalid booking time format")
        
        # Check if pickup is required but not offered
        if pickup_required and not service.offers_pickup:
            raise ValueError("This service does not offer pickup")
        
        # Calculate total charge
        total_charge = service.get_total_charge(pickup_required)
        
        # Validate pickup address if pickup required
        if pickup_required and not pickup_address:
            raise ValueError("Pickup address is required when pickup is requested")
        
        # Verify wallet has sufficient funds
        wallet = self.wallet_service.get_wallet_by_user_id(user_id)
        if not wallet or not wallet.has_sufficient_funds(total_charge):
            raise ValueError("Insufficient funds in wallet")
        
        try:
            # Process payment
            payment_success = self.wallet_service.transfer_payment(
                from_user_id=user_id,
                to_user_id=service.provider_id,
                amount=total_charge,
                reference_id=f"mechanical_booking_{user_id}_{service_id}_{datetime.utcnow().timestamp()}"
            )
            
            if not payment_success:
                raise ValueError("Payment processing failed")
            
            # Create booking
            booking = self.booking_repository.create_booking(
                user_id=user_id,
                service_id=service_id,
                booking_time=booking_time,
                amount=total_charge,
                status=BookingStatus.PENDING
            )
            
            # Set additional data
            additional_data = {}
            if vehicle_details:
                additional_data['vehicle_details'] = vehicle_details
            if issue_description:
                additional_data['issue_description'] = issue_description
            if pickup_required:
                additional_data['pickup_required'] = pickup_required
                additional_data['pickup_address'] = pickup_address
            
            booking.additional_data = str(additional_data) if additional_data else None
            
            # Save booking
            return self.booking_repository.update(booking)
            
        except Exception as e:
            db.session.rollback()
            raise e
