from datetime import datetime
from models.car_pool import CarPoolService as CarPoolServiceModel, BikePoolService as BikePoolServiceModel
from models.booking import Booking
from models.enum_types import ServiceType, BookingStatus, VehicleType
from repositories.car_pool_repository import CarPoolRepository
from repositories.booking_repository import BookingRepository
from services.wallet_service import WalletService
from app import db

class CarPoolService:
    def __init__(self):
        self.car_pool_repository = CarPoolRepository()
        self.booking_repository = BookingRepository()
        self.wallet_service = WalletService()
    
    def get_car_pool_services(self, vehicle_type=None, source=None, destination=None, date=None):
        """
        Get car/bike pool services, optionally filtered
        
        Args:
            vehicle_type: Filter by vehicle type (optional)
            source: Filter by source location (optional)
            destination: Filter by destination (optional)
            date: Filter by departure date (optional)
            
        Returns:
            List of car/bike pool service objects
        """
        return self.car_pool_repository.find_all(
            vehicle_type=vehicle_type,
            source=source,
            destination=destination,
            date=date
        )
    
    def create_car_pool_service(self, name, description, provider_id, vehicle_type, price,
                               source, destination, departure_time, total_seats,
                               vehicle_model=None, vehicle_number=None):
        """
        Create a new car/bike pool service
        
        Args:
            name: Service name
            description: Service description
            provider_id: ID of the service provider
            vehicle_type: Type of vehicle (CAR/BIKE)
            price: Price per seat
            source: Starting location
            destination: Ending location
            departure_time: Departure date and time
            total_seats: Total seats available
            vehicle_model: Vehicle model (optional)
            vehicle_number: Vehicle registration number (optional)
            
        Returns:
            Newly created car/bike pool service object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        if not source or not destination or not departure_time:
            raise ValueError("Source, destination, and departure time are required")
        
        if not total_seats or total_seats <= 0:
            raise ValueError("Total seats must be positive")
        
        # Parse departure time
        if isinstance(departure_time, str):
            try:
                departure_time = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("Invalid departure time format")
        
        # Create appropriate service based on vehicle type
        if vehicle_type == VehicleType.CAR:
            service = CarPoolServiceModel(
                name=name,
                description=description,
                provider_id=provider_id,
                price=price,
                vehicle_type=vehicle_type,
                source=source,
                destination=destination,
                departure_time=departure_time,
                total_seats=total_seats,
                vehicle_model=vehicle_model,
                vehicle_number=vehicle_number
            )
        elif vehicle_type == VehicleType.BIKE:
            service = BikePoolServiceModel(
                name=name,
                description=description,
                provider_id=provider_id,
                price=price,
                source=source,
                destination=destination,
                departure_time=departure_time,
                total_seats=total_seats,
                vehicle_model=vehicle_model,
                vehicle_number=vehicle_number
            )
        else:
            raise ValueError(f"Invalid vehicle type: {vehicle_type}")
        
        # Save service
        return self.car_pool_repository.create(service)
    
    def update_car_pool_service(self, service_id, provider_id, data):
        """
        Update a car/bike pool service
        
        Args:
            service_id: ID of the service to update
            provider_id: ID of the service provider (for authorization)
            data: Dictionary of fields to update
            
        Returns:
            Updated car/bike pool service object
            
        Raises:
            ValueError: If service not found or provider not authorized
        """
        # Get service
        service = self.car_pool_repository.find_by_id(service_id)
        if not service:
            raise ValueError(f"Car pool service with ID {service_id} not found")
        
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
        
        # Update car pool specific fields
        if 'source' in data:
            service.source = data['source']
        if 'destination' in data:
            service.destination = data['destination']
        if 'departure_time' in data:
            departure_time = data['departure_time']
            if isinstance(departure_time, str):
                try:
                    departure_time = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
                except ValueError:
                    raise ValueError("Invalid departure time format")
            service.departure_time = departure_time
        if 'vehicle_model' in data:
            service.vehicle_model = data['vehicle_model']
        if 'vehicle_number' in data:
            service.vehicle_number = data['vehicle_number']
        
        # Don't allow updating total_seats if some seats are already booked
        if 'total_seats' in data:
            new_total_seats = int(data['total_seats'])
            if new_total_seats < service.total_seats - service.available_seats:
                raise ValueError("Cannot reduce total seats below number of already booked seats")
            
            # Update available seats accordingly
            seats_difference = new_total_seats - service.total_seats
            service.total_seats = new_total_seats
            service.available_seats += seats_difference
        
        # Save updated service
        return self.car_pool_repository.update(service)
    
    def book_car_pool_service(self, user_id, service_id, num_seats=1):
        """
        Book seats in a car/bike pool service
        
        Args:
            user_id: ID of the user booking the service
            service_id: ID of the service to book
            num_seats: Number of seats to book
            
        Returns:
            Newly created booking object
            
        Raises:
            ValueError: If service not found, insufficient seats, or other validation fails
        """
        # Validate num_seats
        if num_seats <= 0:
            raise ValueError("Number of seats must be positive")
        
        # Get service
        service = self.car_pool_repository.find_by_id(service_id)
        if not service:
            raise ValueError(f"Car pool service with ID {service_id} not found")
        
        # Check if enough seats are available
        if service.available_seats < num_seats:
            raise ValueError(f"Not enough seats available. Requested: {num_seats}, Available: {service.available_seats}")
        
        # Calculate total price
        total_price = float(service.price) * num_seats
        
        # Verify wallet has sufficient funds
        wallet = self.wallet_service.get_wallet_by_user_id(user_id)
        if not wallet or not wallet.has_sufficient_funds(total_price):
            raise ValueError("Insufficient funds in wallet")
        
        try:
            # Process payment
            payment_success = self.wallet_service.transfer_payment(
                from_user_id=user_id,
                to_user_id=service.provider_id,
                amount=total_price,
                reference_id=f"car_pool_booking_{user_id}_{service_id}_{datetime.utcnow().timestamp()}"
            )
            
            if not payment_success:
                raise ValueError("Payment processing failed")
            
            # Book seats
            service.book_seat(num_seats)
            self.car_pool_repository.update(service)
            
            # Create booking
            booking = Booking(
                user_id=user_id,
                service_id=service_id,
                booking_time=service.departure_time,
                amount=total_price
            )
            
            # Additional data for car pool bookings
            booking.additional_data = f"Seats: {num_seats}"
            
            # Save booking
            return self.booking_repository.create(booking)
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def cancel_car_pool_booking(self, booking_id, user_id):
        """
        Cancel a car/bike pool booking
        
        Args:
            booking_id: ID of the booking to cancel
            user_id: ID of the user cancelling the booking
            
        Returns:
            Updated booking object
            
        Raises:
            ValueError: If booking not found or user not authorized
        """
        # Get booking
        booking = self.booking_repository.find_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking with ID {booking_id} not found")
        
        # Check if user is authorized to cancel
        if booking.user_id != user_id:
            raise ValueError("Not authorized to cancel this booking")
        
        # Check if booking can be cancelled
        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            raise ValueError(f"Booking with status {booking.status} cannot be cancelled")
        
        # Get service
        service = self.car_pool_repository.find_by_id(booking.service_id)
        if not service:
            raise ValueError(f"Car pool service with ID {booking.service_id} not found")
        
        try:
            # Process refund
            self.wallet_service.refund_payment(
                user_id=user_id,
                amount=float(booking.amount),
                reference_id=str(booking_id),
                description=f"Refund for cancelled car pool booking #{booking_id}"
            )
            
            # Extract number of seats from additional_data
            num_seats = 1  # Default
            if booking.additional_data and "Seats:" in booking.additional_data:
                try:
                    num_seats = int(booking.additional_data.split("Seats:")[1].strip())
                except:
                    pass
            
            # Release seats
            service.release_seat(num_seats)
            self.car_pool_repository.update(service)
            
            # Update booking status
            booking.status = BookingStatus.CANCELLED
            
            # Save updated booking
            return self.booking_repository.update(booking)
            
        except Exception as e:
            db.session.rollback()
            raise e
