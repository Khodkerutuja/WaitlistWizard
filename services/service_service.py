from datetime import datetime
from models.service import Service, Booking, ServiceStatus, BookingStatus
from models.car_pool import CarPoolService, BikePoolService
from models.gym import GymService, GymSubscription
from models.household import HouseholdService
from models.mechanical import MechanicalService
from models.user import User, UserRole, UserStatus
from repositories.service_repository import ServiceRepository
from repositories.booking_repository import BookingRepository
from repositories.user_repository import UserRepository
from services.wallet_service import WalletService
from app import db

class ServiceService:
    def __init__(self):
        self.service_repository = ServiceRepository()
        self.booking_repository = BookingRepository()
        self.user_repository = UserRepository()
        self.wallet_service = WalletService()
    
    def get_all_services(self, service_type=None, status=None, provider_id=None):
        """
        Get all services, optionally filtered by type, status, and/or provider
        
        Args:
            service_type: Filter by service type (optional)
            status: Filter by status (optional)
            provider_id: Filter by provider ID (optional)
            
        Returns:
            List of service objects
        """
        # Default status to AVAILABLE if not specified
        if status is None:
            status = ServiceStatus.AVAILABLE
            
        return self.service_repository.find_all(
            service_type=service_type,
            status=status,
            provider_id=provider_id
        )
    
    def get_service_by_id(self, service_id):
        """
        Get a service by ID
        
        Args:
            service_id: ID of the service to fetch
            
        Returns:
            Service object if found, None otherwise
        """
        return self.service_repository.find_by_id(service_id)
    
    def create_service(self, name, description, provider_id, service_type, price, 
                       location=None, availability=None, additional_data=None):
        """
        Create a new service
        
        Args:
            name: Service name
            description: Service description
            provider_id: ID of the service provider
            service_type: Type of service
            price: Base price of the service
            location: Service location (optional)
            availability: Service availability (optional)
            additional_data: Additional service-specific data (optional)
            
        Returns:
            Newly created service object
            
        Raises:
            ValueError: If provider not found or other validation fails
        """
        # Check if provider exists and is active
        provider = self.user_repository.find_by_id(provider_id)
        if not provider:
            raise ValueError(f"Provider with ID {provider_id} not found")
        
        if provider.role != UserRole.POWER_USER:
            raise ValueError(f"User with ID {provider_id} is not a service provider")
        
        if provider.status != UserStatus.ACTIVE:
            raise ValueError(f"Provider with ID {provider_id} is not active")
        
        # Create specific service based on type
        if service_type in ['CAR_POOL', 'BIKE_POOL', 'GYM_FITNESS', 'HOUSEHOLD', 'MECHANICAL']:
            # Delegate to specific service creation functions
            if service_type == 'CAR_POOL' or service_type == 'BIKE_POOL':
                from services.car_pool_service import CarPoolService
                car_pool_service = CarPoolService()
                return car_pool_service.create_car_pool_service(
                    name=name,
                    description=description,
                    provider_id=provider_id,
                    vehicle_type='CAR' if service_type == 'CAR_POOL' else 'BIKE',
                    price=price,
                    source=additional_data.get('source'),
                    destination=additional_data.get('destination'),
                    departure_time=additional_data.get('departure_time'),
                    total_seats=additional_data.get('total_seats'),
                    vehicle_model=additional_data.get('vehicle_model'),
                    vehicle_number=additional_data.get('vehicle_number')
                )
                
            elif service_type == 'GYM_FITNESS':
                from services.gym_service import GymService
                gym_service = GymService()
                return gym_service.create_gym_service(
                    name=name,
                    description=description,
                    provider_id=provider_id,
                    gym_name=additional_data.get('gym_name'),
                    facility_types=additional_data.get('facility_types'),
                    operating_hours=additional_data.get('operating_hours'),
                    subscription_plans=additional_data.get('subscription_plans'),
                    trainers_available=additional_data.get('trainers_available', False),
                    dietician_available=additional_data.get('dietician_available', False),
                    location=location
                )
                
            elif service_type == 'HOUSEHOLD':
                from services.household_service import HouseholdService
                household_service = HouseholdService()
                return household_service.create_household_service(
                    name=name,
                    description=description,
                    provider_id=provider_id,
                    household_type=additional_data.get('household_type'),
                    price=price,
                    hourly_rate=additional_data.get('hourly_rate'),
                    visit_charge=additional_data.get('visit_charge'),
                    estimated_duration=additional_data.get('estimated_duration'),
                    location=location,
                    availability=availability
                )
                
            elif service_type == 'MECHANICAL':
                from services.mechanical_service import MechanicalService
                mechanical_service = MechanicalService()
                return mechanical_service.create_mechanical_service(
                    name=name,
                    description=description,
                    provider_id=provider_id,
                    mechanical_type=additional_data.get('mechanical_type'),
                    service_charge=price,
                    additional_charges_desc=additional_data.get('additional_charges_desc'),
                    estimated_time=additional_data.get('estimated_time'),
                    offers_pickup=additional_data.get('offers_pickup', False),
                    pickup_charge=additional_data.get('pickup_charge'),
                    location=location,
                    availability=availability
                )
        else:
            # Create generic service
            service = Service(
                name=name,
                description=description,
                provider_id=provider_id,
                service_type=service_type,
                price=price,
                location=location,
                availability=availability
            )
            
            # Save service
            return self.service_repository.create(service)
    
    def update_service(self, service_id, data):
        """
        Update a service
        
        Args:
            service_id: ID of the service to update
            data: Dictionary of fields to update
            
        Returns:
            Updated service object
            
        Raises:
            ValueError: If service not found
        """
        service = self.service_repository.find_by_id(service_id)
        if not service:
            raise ValueError(f"Service with ID {service_id} not found")
        
        # Update base service fields
        if 'name' in data:
            service.name = data['name']
        if 'description' in data:
            service.description = data['description']
        if 'price' in data:
            service.price = data['price']
        if 'status' in data:
            service.status = data['status']
        if 'location' in data:
            service.location = data['location']
        if 'availability' in data:
            service.availability = data['availability']
        
        # Specific service type updates will be handled by specific services
        if service.service_type == 'CAR_POOL' or service.service_type == 'BIKE_POOL':
            from services.car_pool_service import CarPoolService
            car_pool_service = CarPoolService()
            return car_pool_service.update_car_pool_service(
                service_id=service_id,
                provider_id=service.provider_id,
                data=data
            )
            
        elif service.service_type == 'GYM_FITNESS':
            from services.gym_service import GymService
            gym_service = GymService()
            return gym_service.update_gym_service(
                service_id=service_id,
                provider_id=service.provider_id,
                data=data
            )
            
        elif service.service_type == 'HOUSEHOLD':
            from services.household_service import HouseholdService
            household_service = HouseholdService()
            return household_service.update_household_service(
                service_id=service_id,
                provider_id=service.provider_id,
                data=data
            )
            
        elif service.service_type == 'MECHANICAL':
            from services.mechanical_service import MechanicalService
            mechanical_service = MechanicalService()
            return mechanical_service.update_mechanical_service(
                service_id=service_id,
                provider_id=service.provider_id,
                data=data
            )
        
        # Save updated service
        return self.service_repository.update(service)
    
    def delete_service(self, service_id):
        """
        Delete a service (mark as DELETED)
        
        Args:
            service_id: ID of the service to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            ValueError: If service not found
        """
        service = self.service_repository.find_by_id(service_id)
        if not service:
            raise ValueError(f"Service with ID {service_id} not found")
        
        # Mark as deleted
        service.status = ServiceStatus.DELETED
        
        # Save updated service
        self.service_repository.update(service)
        return True
    
    def book_service(self, user_id, service_id, booking_time, additional_data=None):
        """
        Book a service
        
        Args:
            user_id: ID of the user booking the service
            service_id: ID of the service to book
            booking_time: Date and time of the booking
            additional_data: Additional booking data
            
        Returns:
            Newly created booking object
            
        Raises:
            ValueError: If user or service not found, or other validation fails
        """
        # Check if user exists
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Check if service exists and is available
        service = self.service_repository.find_by_id(service_id)
        if not service:
            raise ValueError(f"Service with ID {service_id} not found")
        
        if service.status != ServiceStatus.AVAILABLE:
            raise ValueError(f"Service with ID {service_id} is not available")
        
        # Delegate to specific booking functions based on service type
        if service.service_type == 'CAR_POOL' or service.service_type == 'BIKE_POOL':
            from services.car_pool_service import CarPoolService
            car_pool_service = CarPoolService()
            num_seats = additional_data.get('num_seats', 1) if additional_data else 1
            return car_pool_service.book_car_pool_service(
                user_id=user_id,
                service_id=service_id,
                num_seats=num_seats
            )
            
        elif service.service_type == 'GYM_FITNESS':
            from services.gym_service import GymService
            gym_service = GymService()
            subscription_plan = additional_data.get('subscription_plan') if additional_data else None
            if not subscription_plan:
                raise ValueError("Subscription plan is required for gym bookings")
                
            return gym_service.subscribe_to_gym(
                user_id=user_id,
                service_id=service_id,
                subscription_plan=subscription_plan,
                trainer_required=additional_data.get('trainer_required', False) if additional_data else False,
                dietician_required=additional_data.get('dietician_required', False) if additional_data else False
            )
            
        elif service.service_type == 'HOUSEHOLD':
            from services.household_service import HouseholdService
            household_service = HouseholdService()
            return household_service.book_household_service(
                user_id=user_id,
                service_id=service_id,
                booking_time=booking_time,
                hours=additional_data.get('hours') if additional_data else None,
                address=additional_data.get('address') if additional_data else None
            )
            
        elif service.service_type == 'MECHANICAL':
            from services.mechanical_service import MechanicalService
            mechanical_service = MechanicalService()
            return mechanical_service.book_mechanical_service(
                user_id=user_id,
                service_id=service_id,
                booking_time=booking_time,
                vehicle_details=additional_data.get('vehicle_details') if additional_data else None,
                issue_description=additional_data.get('issue_description') if additional_data else None,
                pickup_required=additional_data.get('pickup_required', False) if additional_data else False,
                pickup_address=additional_data.get('pickup_address') if additional_data else None
            )
        
        # Generic booking for other service types
        # Verify wallet has sufficient funds
        wallet = self.wallet_service.get_wallet_by_user_id(user_id)
        if not wallet or not wallet.has_sufficient_funds(float(service.price)):
            raise ValueError("Insufficient funds in wallet")
        
        try:
            # Process payment
            payment_success = self.wallet_service.transfer_payment(
                from_user_id=user_id,
                to_user_id=service.provider_id,
                amount=float(service.price),
                reference_id=f"booking_{user_id}_{service_id}_{datetime.utcnow().timestamp()}"
            )
            
            if not payment_success:
                raise ValueError("Payment processing failed")
            
            # Create booking
            booking = Booking(
                user_id=user_id,
                service_id=service_id,
                booking_time=datetime.fromisoformat(booking_time.replace('Z', '+00:00')),
                amount=service.price
            )
            
            # Save booking
            return self.booking_repository.create(booking)
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_user_bookings(self, user_id, status=None):
        """
        Get bookings for a user
        
        Args:
            user_id: ID of the user
            status: Filter by booking status (optional)
            
        Returns:
            List of booking objects
        """
        return self.booking_repository.find_by_user_id(user_id, status)
    
    def get_provider_bookings(self, provider_id, status=None):
        """
        Get bookings for a service provider
        
        Args:
            provider_id: ID of the service provider
            status: Filter by booking status (optional)
            
        Returns:
            List of booking objects
        """
        return self.booking_repository.find_by_provider_id(provider_id, status)
    
    def cancel_booking(self, booking_id, user_id):
        """
        Cancel a booking
        
        Args:
            booking_id: ID of the booking to cancel
            user_id: ID of the user cancelling the booking
            
        Returns:
            Updated booking object
            
        Raises:
            ValueError: If booking not found or user not authorized
        """
        booking = self.booking_repository.find_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking with ID {booking_id} not found")
        
        # Check if user is authorized to cancel
        if booking.user_id != user_id:
            raise ValueError("Not authorized to cancel this booking")
        
        # Check if booking can be cancelled
        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            raise ValueError(f"Booking with status {booking.status} cannot be cancelled")
        
        try:
            # Process refund
            self.wallet_service.refund_payment(
                user_id=user_id,
                amount=float(booking.amount),
                reference_id=str(booking_id),
                description=f"Refund for cancelled booking #{booking_id}"
            )
            
            # Update booking status
            booking.status = BookingStatus.CANCELLED
            
            # Save updated booking
            return self.booking_repository.update(booking)
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def update_booking_status(self, booking_id, provider_id, status):
        """
        Update booking status by service provider
        
        Args:
            booking_id: ID of the booking to update
            provider_id: ID of the service provider
            status: New booking status
            
        Returns:
            Updated booking object
            
        Raises:
            ValueError: If booking not found, provider not authorized, or invalid status
        """
        booking = self.booking_repository.find_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking with ID {booking_id} not found")
        
        # Get service
        service = self.service_repository.find_by_id(booking.service_id)
        if not service:
            raise ValueError(f"Service with ID {booking.service_id} not found")
        
        # Check if provider is authorized
        if service.provider_id != provider_id:
            raise ValueError("Not authorized to update this booking")
        
        # Validate status
        if status not in [BookingStatus.CONFIRMED, BookingStatus.REJECTED, BookingStatus.COMPLETED]:
            raise ValueError(f"Invalid status: {status}")
        
        # Handle rejection - process refund
        if status == BookingStatus.REJECTED and booking.status != BookingStatus.REJECTED:
            try:
                self.wallet_service.refund_payment(
                    user_id=booking.user_id,
                    amount=float(booking.amount),
                    reference_id=str(booking_id),
                    description=f"Refund for rejected booking #{booking_id}"
                )
            except Exception as e:
                db.session.rollback()
                raise e
        
        # Update booking status
        booking.status = status
        
        # Save updated booking
        return self.booking_repository.update(booking)
