from datetime import datetime
from models.household import HouseholdService, HouseholdServiceType
from models.service import BookingStatus
from repositories.household_repository import HouseholdRepository
from repositories.booking_repository import BookingRepository
from services.wallet_service import WalletService
from app import db

class HouseholdService:
    def __init__(self):
        self.household_repository = HouseholdRepository()
        self.booking_repository = BookingRepository()
        self.wallet_service = WalletService()
    
    def get_household_services(self, household_type=None, location=None):
        """
        Get household services, optionally filtered
        
        Args:
            household_type: Filter by household service type (optional)
            location: Filter by location (optional)
            
        Returns:
            List of household service objects
        """
        return self.household_repository.find_all(
            household_type=household_type,
            location=location
        )
    
    def create_household_service(self, name, description, provider_id, household_type, price,
                               hourly_rate=None, visit_charge=None, estimated_duration=None,
                               location=None, availability=None):
        """
        Create a new household service
        
        Args:
            name: Service name
            description: Service description
            provider_id: ID of the service provider
            household_type: Type of household service
            price: Base price of the service
            hourly_rate: Hourly rate (optional)
            visit_charge: Fixed charge per visit (optional)
            estimated_duration: Estimated duration in minutes (optional)
            location: Service location (optional)
            availability: Service availability (optional)
            
        Returns:
            Newly created household service object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate household type
        if household_type not in [HouseholdServiceType.MAID, HouseholdServiceType.PLUMBING, 
                                 HouseholdServiceType.ELECTRICAL, HouseholdServiceType.PEST_CONTROL, 
                                 HouseholdServiceType.CLEANING, HouseholdServiceType.OTHER]:
            raise ValueError(f"Invalid household service type: {household_type}")
        
        # Ensure at least one pricing model is provided
        if price <= 0 and not hourly_rate and not visit_charge:
            raise ValueError("At least one pricing model (price, hourly_rate, or visit_charge) must be provided")
        
        # Create household service
        service = HouseholdService(
            name=name,
            description=description,
            provider_id=provider_id,
            price=price,
            household_type=household_type,
            hourly_rate=hourly_rate,
            visit_charge=visit_charge,
            estimated_duration=estimated_duration,
            location=location,
            availability=availability
        )
        
        # Save service
        return self.household_repository.create(service)
    
    def update_household_service(self, service_id, provider_id, data):
        """
        Update a household service
        
        Args:
            service_id: ID of the service to update
            provider_id: ID of the service provider (for authorization)
            data: Dictionary of fields to update
            
        Returns:
            Updated household service object
            
        Raises:
            ValueError: If service not found or provider not authorized
        """
        # Get service
        service = self.household_repository.find_by_id(service_id)
        if not service:
            raise ValueError(f"Household service with ID {service_id} not found")
        
        # Check if provider is authorized
        if service.provider_id != provider_id:
            raise ValueError("Not authorized to update this service")
        
        # Update base service fields
        if 'name' in data:
            service.name = data['name']
        if 'description' in data:
            service.description = data['description']
        if 'price' in data:
            service.price = data['price']
        
        # Update household service specific fields
        if 'hourly_rate' in data:
            service.hourly_rate = data['hourly_rate']
        if 'visit_charge' in data:
            service.visit_charge = data['visit_charge']
        if 'estimated_duration' in data:
            service.estimated_duration = data['estimated_duration']
        if 'location' in data:
            service.location = data['location']
        if 'availability' in data:
            service.availability = data['availability']
        
        # Save updated service
        return self.household_repository.update(service)
    
    def book_household_service(self, user_id, service_id, booking_time, hours=None, address=None):
        """
        Book a household service
        
        Args:
            user_id: ID of the user booking the service
            service_id: ID of the service to book
            booking_time: Date and time of the booking
            hours: Number of hours for hourly services (optional)
            address: Service delivery address (optional)
            
        Returns:
            Newly created booking object
            
        Raises:
            ValueError: If service not found, invalid booking details, or other validation fails
        """
        # Get service
        service = self.household_repository.find_by_id(service_id)
        if not service:
            raise ValueError(f"Household service with ID {service_id} not found")
        
        # Parse booking time
        if isinstance(booking_time, str):
            try:
                booking_time = datetime.fromisoformat(booking_time.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("Invalid booking time format")
        
        # Calculate total cost
        if service.hourly_rate and hours is None:
            raise ValueError("Hours must be provided for hourly rate services")
        
        total_cost = service.calculate_total_cost(hours)
        if total_cost <= 0:
            raise ValueError("Service cost must be positive")
        
        # Verify wallet has sufficient funds
        wallet = self.wallet_service.get_wallet_by_user_id(user_id)
        if not wallet or not wallet.has_sufficient_funds(total_cost):
            raise ValueError("Insufficient funds in wallet")
        
        try:
            # Process payment
            payment_success = self.wallet_service.transfer_payment(
                from_user_id=user_id,
                to_user_id=service.provider_id,
                amount=total_cost,
                reference_id=f"household_booking_{user_id}_{service_id}_{datetime.utcnow().timestamp()}"
            )
            
            if not payment_success:
                raise ValueError("Payment processing failed")
            
            # Create booking
            booking = self.booking_repository.create_booking(
                user_id=user_id,
                service_id=service_id,
                booking_time=booking_time,
                amount=total_cost,
                status=BookingStatus.PENDING
            )
            
            # Set additional data
            additional_data = {}
            if hours:
                additional_data['hours'] = hours
            if address:
                additional_data['address'] = address
            
            booking.additional_data = str(additional_data) if additional_data else None
            
            # Save booking
            return self.booking_repository.update(booking)
            
        except Exception as e:
            db.session.rollback()
            raise e
