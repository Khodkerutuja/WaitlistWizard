from app import app, db
from werkzeug.security import generate_password_hash
from models.user import User, UserRole, UserStatus
from models.service import Service, ServiceStatus, ServiceType
from models.wallet import Wallet
from models.car_pool import CarPoolService, VehicleType
from models.gym import GymService
from models.household import HouseholdService, HouseholdServiceType
from models.mechanical import MechanicalService, MechanicalServiceType
from datetime import datetime

def create_test_data(force=False):
    """Create test data for the application"""
    with app.app_context():
        # Check if data already exists
        if User.query.count() > 0 and not force:
            print("Data already exists, skipping seed.")
            return
            
        # Clear existing data if force is true
        if force:
            print("Clearing existing data...")
            try:
                db.session.query(MechanicalService).delete()
                db.session.query(HouseholdService).delete()
                db.session.query(GymService).delete()
                db.session.query(CarPoolService).delete()
                db.session.query(Service).delete()
                db.session.query(Wallet).delete()
                db.session.query(User).delete()
                db.session.commit()
                print("Existing data cleared successfully.")
            except Exception as e:
                db.session.rollback()
                print(f"Error clearing data: {e}")
        
        print("Creating test data...")
        
        # Create users
        admin_user = User(
            email="admin@example.com",
            password="password123",
            first_name="Admin",
            last_name="User",
            phone_number="1234567890",
            role=UserRole.ADMIN
        )
        
        service_provider1 = User(
            email="provider1@example.com",
            password="password123",
            first_name="John",
            last_name="Doe",
            phone_number="9876543210",
            role=UserRole.POWER_USER
        )
        service_provider1.service_type = "CAR_POOL"
        service_provider1.description = "Experienced driver offering car pooling services."
        
        service_provider2 = User(
            email="provider2@example.com",
            password="password123",
            first_name="Jane",
            last_name="Smith",
            phone_number="5678901234",
            role=UserRole.POWER_USER
        )
        service_provider2.service_type = "GYM_FITNESS"
        service_provider2.description = "Certified personal trainer with 5 years of experience."
        
        service_provider3 = User(
            email="provider3@example.com",
            password="password123",
            first_name="Alex",
            last_name="Johnson",
            phone_number="1290345678",
            role=UserRole.POWER_USER
        )
        service_provider3.service_type = "HOUSEHOLD"
        service_provider3.description = "Professional cleaner and housekeeper."
        
        service_provider4 = User(
            email="provider4@example.com",
            password="password123",
            first_name="Michael",
            last_name="Brown",
            phone_number="3456789012",
            role=UserRole.POWER_USER
        )
        service_provider4.service_type = "MECHANICAL"
        service_provider4.description = "Certified mechanic with 10 years of experience."
        
        regular_user = User(
            email="user@example.com",
            password="password123",
            first_name="Robert",
            last_name="Williams",
            phone_number="6789012345",
            role=UserRole.USER
        )
        
        # Add users to database
        db.session.add_all([admin_user, service_provider1, service_provider2, 
                           service_provider3, service_provider4, regular_user])
        db.session.commit()
        
        # Create wallets for all users
        users = User.query.all()
        for user in users:
            wallet = Wallet(user_id=user.id, initial_balance=1000)
            db.session.add(wallet)
        
        db.session.commit()
        
        # Create services using the specific model classes instead of base Service class
        # This ensures polymorphic attributes are properly set

        # Car Pool Services
        departure_time1 = datetime.strptime("2025-04-02 08:00:00", "%Y-%m-%d %H:%M:%S")
        departure_time2 = datetime.strptime("2025-04-03 09:00:00", "%Y-%m-%d %H:%M:%S")
        
        car_service1 = CarPoolService(
            name="Daily Commute - Central to Suburb",
            description="Daily car pool from central area to northern suburbs. Comfortable sedan with AC.",
            provider_id=service_provider1.id,
            price=250.00,
            vehicle_type=VehicleType.CAR,
            source="Central City",
            destination="Northern Suburbs",
            departure_time=departure_time1,
            total_seats=4,
            vehicle_model="Honda City",
            vehicle_number="AB1234"
        )
        car_service1.status = ServiceStatus.AVAILABLE
        
        car_service2 = CarPoolService(
            name="Weekend Getaway - City to Beach",
            description="Weekend car pool to the beach. SUV with ample space for luggage.",
            provider_id=service_provider1.id,
            price=500.00,
            vehicle_type=VehicleType.CAR,
            source="City Center",
            destination="Beach Resort",
            departure_time=departure_time2,
            total_seats=6,
            vehicle_model="Toyota Fortuner",
            vehicle_number="XY5678"
        )
        car_service2.status = ServiceStatus.AVAILABLE
        car_service2.location = "City Center" 
        
        # Gym & Fitness Services
        gym_service1 = GymService(
            name="Personal Training Sessions",
            description="One-on-one personal training sessions tailored to your fitness goals.",
            provider_id=service_provider2.id,
            gym_name="FitZone Gym",
            facility_types=["Cardio", "Weights", "Personal Training"],
            operating_hours={"weekday": "6:00 AM - 9:00 PM", "weekend": "8:00 AM - 6:00 PM"},
            subscription_plans={"MONTHLY": 800, "QUARTERLY": 2200, "ANNUAL": 8000},
            trainers_available=True
        )
        gym_service1.status = ServiceStatus.AVAILABLE
        gym_service1.location = "FitZone Gym, Downtown"
        
        gym_service2 = GymService(
            name="Group Yoga Classes",
            description="Group yoga sessions for all experience levels.",
            provider_id=service_provider2.id,
            gym_name="Serene Yoga Studio",
            facility_types=["Yoga", "Meditation", "Pilates"],
            operating_hours={"weekday": "7:00 AM - 8:00 PM", "weekend": "8:00 AM - 5:00 PM"},
            subscription_plans={"MONTHLY": 400, "QUARTERLY": 1100, "ANNUAL": 4000},
            trainers_available=True
        )
        gym_service2.status = ServiceStatus.AVAILABLE
        gym_service2.location = "Serene Yoga Studio, West End"
        
        # Household Services
        household_service1 = HouseholdService(
            name="Deep House Cleaning",
            description="Comprehensive house cleaning service including all rooms and bathrooms.",
            provider_id=service_provider3.id,
            price=1500.00,
            household_type=HouseholdServiceType.CLEANING,
            hourly_rate=300.00,
            visit_charge=500.00,
            estimated_duration=240,  # 4 hours in minutes
            location="Client's Home"
        )
        household_service1.status = ServiceStatus.AVAILABLE
        
        household_service2 = HouseholdService(
            name="Garden Maintenance",
            description="Garden maintenance including lawn mowing, trimming, and general maintenance.",
            provider_id=service_provider3.id,
            price=800.00,
            household_type=HouseholdServiceType.OTHER,
            hourly_rate=200.00,
            visit_charge=300.00,
            estimated_duration=180,  # 3 hours in minutes
            location="Client's Garden"
        )
        household_service2.status = ServiceStatus.AVAILABLE
        
        # Mechanical Services
        mechanical_service1 = MechanicalService(
            name="Car Servicing and Repair",
            description="General car servicing and repair for all makes and models.",
            provider_id=service_provider4.id,
            service_charge=2000.00,
            mechanical_type=MechanicalServiceType.CAR_REPAIR,
            additional_charges_desc="Parts cost extra depending on car model",
            estimated_time=120,  # 2 hours in minutes
            offers_pickup=True,
            pickup_charge=500.00,
            location="Mike's Garage"
        )
        mechanical_service1.status = ServiceStatus.AVAILABLE
        
        mechanical_service2 = MechanicalService(
            name="Bike Tune-up",
            description="Complete tune-up for bikes, including brake adjustment, gear setting, and wheel alignment.",
            provider_id=service_provider4.id,
            service_charge=800.00,
            mechanical_type=MechanicalServiceType.BIKE_REPAIR,
            additional_charges_desc="Parts replacement extra if needed",
            estimated_time=60,  # 1 hour in minutes
            offers_pickup=True,
            pickup_charge=200.00,
            location="Mike's Garage"
        )
        mechanical_service2.status = ServiceStatus.AVAILABLE
        
        # Add services to database
        db.session.add_all([
            car_service1, car_service2,
            gym_service1, gym_service2,
            household_service1, household_service2,
            mechanical_service1, mechanical_service2
        ])
        
        db.session.commit()
        
        # Create bookings
        from models.booking import Booking, BookingStatus
        from models.transaction import Transaction, TransactionType
        
        # Get regular user and their wallet
        user = User.query.filter_by(email="user@example.com").first()
        user_wallet = Wallet.query.filter_by(user_id=user.id).first()
        
        # Create different bookings with different statuses to demonstrate the My Bookings page
        # Pending booking
        pending_booking = Booking(
            service_id=car_service1.id,
            user_id=user.id,
            amount=car_service1.price,
            quantity=1,
            notes="Need pickup at 8:00 AM sharp"
        )
        pending_booking.booking_time = datetime.strptime("2025-04-05 08:00:00", "%Y-%m-%d %H:%M:%S")
        # Status is already PENDING by default
        
        # Confirmed booking
        confirmed_booking = Booking(
            service_id=gym_service1.id,
            user_id=user.id,
            amount=gym_service1.price if hasattr(gym_service1, 'price') and gym_service1.price else 800.00,
            quantity=1,
            notes="Need personal training for weight loss"
        )
        confirmed_booking.booking_time = datetime.strptime("2025-04-06 10:00:00", "%Y-%m-%d %H:%M:%S")
        confirmed_booking.status = BookingStatus.CONFIRMED
        
        # Create transaction for the confirmed booking
        confirm_transaction = Transaction(
            wallet_id=user_wallet.id,
            amount=confirmed_booking.amount,
            transaction_type=TransactionType.PAYMENT,
            description=f"Payment for {gym_service1.name}",
            reference_id="1"  # This will be updated after booking is saved
        )
        
        # Completed booking
        completed_booking = Booking(
            service_id=household_service1.id,
            user_id=user.id,
            amount=household_service1.price,
            quantity=1,
            notes="Please bring eco-friendly cleaning supplies"
        )
        completed_booking.booking_time = datetime.strptime("2025-04-01 09:00:00", "%Y-%m-%d %H:%M:%S")
        completed_booking.status = BookingStatus.COMPLETED
        
        # Create transaction for the completed booking
        complete_transaction = Transaction(
            wallet_id=user_wallet.id,
            amount=completed_booking.amount,
            transaction_type=TransactionType.PAYMENT,
            description=f"Payment for {household_service1.name}",
            reference_id="2"  # This will be updated after booking is saved
        )
        
        # Cancelled booking
        cancelled_booking = Booking(
            service_id=mechanical_service1.id,
            user_id=user.id,
            amount=mechanical_service1.service_charge,
            quantity=1,
            notes="Need full service"
        )
        cancelled_booking.booking_time = datetime.strptime("2025-04-03 14:00:00", "%Y-%m-%d %H:%M:%S")
        cancelled_booking.status = BookingStatus.CANCELLED
        
        # Add bookings to database
        db.session.add_all([
            pending_booking, confirmed_booking, completed_booking, cancelled_booking,
            confirm_transaction, complete_transaction
        ])
        
        db.session.commit()
        
        # Update transaction reference IDs with actual booking IDs
        confirm_transaction.reference_id = str(confirmed_booking.id)
        complete_transaction.reference_id = str(completed_booking.id)
        
        # Link transactions to bookings
        confirmed_booking.transaction_id = confirm_transaction.id
        completed_booking.transaction_id = complete_transaction.id
        
        db.session.commit()
        
        # Provider's bookings
        # Get provider1 and create a booking for them
        provider1 = User.query.filter_by(email="provider1@example.com").first()
        provider1_service = Service.query.filter_by(provider_id=provider1.id).first()
        
        booking_for_provider1 = Booking(
            service_id=provider1_service.id,
            user_id=admin_user.id,  # Admin user books the service
            amount=provider1_service.price if hasattr(provider1_service, 'price') and provider1_service.price else 250.00,
            quantity=1,
            notes="Test booking by admin"
        )
        booking_for_provider1.booking_time = datetime.strptime("2025-04-04 15:00:00", "%Y-%m-%d %H:%M:%S")
        # Status is already PENDING by default
        
        db.session.add(booking_for_provider1)
        db.session.commit()
        
        print("Test data created successfully!")

if __name__ == "__main__":
    create_test_data(force=True)