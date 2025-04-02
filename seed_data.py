from app import app, db
from werkzeug.security import generate_password_hash
from models.user import User, UserRole, UserStatus
from models.service import Service, ServiceStatus
from models.wallet import Wallet

def create_test_data():
    """Create test data for the application"""
    with app.app_context():
        # Check if data already exists
        if User.query.count() > 0:
            print("Data already exists, skipping seed.")
            return
        
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
        
        # Create services
        # Car Pool Services
        car_service1 = Service(
            name="Daily Commute - Central to Suburb",
            description="Daily car pool from central area to northern suburbs. Comfortable sedan with AC.",
            provider_id=service_provider1.id,
            service_type="CAR_POOL",
            price=250.00,
            location="Central City"
        )
        car_service1.status = ServiceStatus.AVAILABLE
        setattr(car_service1, 'source', 'Central City')
        setattr(car_service1, 'destination', 'Northern Suburbs')
        setattr(car_service1, 'departure_time', '08:00 AM')
        setattr(car_service1, 'available_seats', 3)
        setattr(car_service1, 'total_seats', 4)
        setattr(car_service1, 'vehicle_type', 'CAR')
        setattr(car_service1, 'vehicle_model', 'Honda City')
        setattr(car_service1, 'vehicle_number', 'AB1234')
        
        car_service2 = Service(
            name="Weekend Getaway - City to Beach",
            description="Weekend car pool to the beach. SUV with ample space for luggage.",
            provider_id=service_provider1.id,
            service_type="CAR_POOL",
            price=500.00,
            location="City Center"
        )
        car_service2.status = ServiceStatus.AVAILABLE
        setattr(car_service2, 'source', 'City Center')
        setattr(car_service2, 'destination', 'Beach Resort')
        setattr(car_service2, 'departure_time', '09:00 AM')
        setattr(car_service2, 'available_seats', 5)
        setattr(car_service2, 'total_seats', 6)
        setattr(car_service2, 'vehicle_type', 'CAR')
        setattr(car_service2, 'vehicle_model', 'Toyota Fortuner')
        setattr(car_service2, 'vehicle_number', 'XY5678')
        
        # Gym & Fitness Services
        gym_service1 = Service(
            name="Personal Training Sessions",
            description="One-on-one personal training sessions tailored to your fitness goals.",
            provider_id=service_provider2.id,
            service_type="GYM_FITNESS",
            price=800.00,
            location="FitZone Gym"
        )
        gym_service1.status = ServiceStatus.AVAILABLE
        setattr(gym_service1, 'location', 'FitZone Gym, Downtown')
        setattr(gym_service1, 'operating_hours', '6:00 AM - 9:00 PM')
        setattr(gym_service1, 'trainer_experience', 5)
        setattr(gym_service1, 'category', 'Personal Training')
        
        gym_service2 = Service(
            name="Group Yoga Classes",
            description="Group yoga sessions for all experience levels.",
            provider_id=service_provider2.id,
            service_type="GYM_FITNESS",
            price=400.00,
            location="Serene Yoga Studio"
        )
        gym_service2.status = ServiceStatus.AVAILABLE
        setattr(gym_service2, 'location', 'Serene Yoga Studio, West End')
        setattr(gym_service2, 'operating_hours', '7:00 AM - 8:00 PM')
        setattr(gym_service2, 'trainer_experience', 8)
        setattr(gym_service2, 'category', 'Yoga')
        
        # Household Services
        household_service1 = Service(
            name="Deep House Cleaning",
            description="Comprehensive house cleaning service including all rooms and bathrooms.",
            provider_id=service_provider3.id,
            service_type="HOUSEHOLD",
            price=1500.00,
            location="Client's Home"
        )
        household_service1.status = ServiceStatus.AVAILABLE
        setattr(household_service1, 'category', 'Cleaning')
        setattr(household_service1, 'estimated_time', 4)
        setattr(household_service1, 'experience', 6)
        setattr(household_service1, 'service_area', 'All City Areas')
        
        household_service2 = Service(
            name="Garden Maintenance",
            description="Garden maintenance including lawn mowing, trimming, and general maintenance.",
            provider_id=service_provider3.id,
            service_type="HOUSEHOLD",
            price=800.00,
            location="Client's Garden"
        )
        household_service2.status = ServiceStatus.AVAILABLE
        setattr(household_service2, 'category', 'Gardening')
        setattr(household_service2, 'estimated_time', 3)
        setattr(household_service2, 'experience', 5)
        setattr(household_service2, 'service_area', 'Suburban Areas')
        
        # Mechanical Services
        mechanical_service1 = Service(
            name="Car Servicing and Repair",
            description="General car servicing and repair for all makes and models.",
            provider_id=service_provider4.id,
            service_type="MECHANICAL",
            price=2000.00,
            location="Mike's Garage"
        )
        mechanical_service1.status = ServiceStatus.AVAILABLE
        setattr(mechanical_service1, 'specialization', 'Car Repair')
        setattr(mechanical_service1, 'vehicle_types', 'All Cars')
        setattr(mechanical_service1, 'experience', 10)
        setattr(mechanical_service1, 'workshop_location', 'East Industrial Zone')
        
        mechanical_service2 = Service(
            name="Bike Tune-up",
            description="Complete tune-up for bikes, including brake adjustment, gear setting, and wheel alignment.",
            provider_id=service_provider4.id,
            service_type="MECHANICAL",
            price=800.00,
            location="Mike's Garage"
        )
        mechanical_service2.status = ServiceStatus.AVAILABLE
        setattr(mechanical_service2, 'specialization', 'Bike Repair')
        setattr(mechanical_service2, 'vehicle_types', 'All Bikes')
        setattr(mechanical_service2, 'experience', 8)
        setattr(mechanical_service2, 'workshop_location', 'East Industrial Zone')
        
        # Add services to database
        db.session.add_all([
            car_service1, car_service2,
            gym_service1, gym_service2,
            household_service1, household_service2,
            mechanical_service1, mechanical_service2
        ])
        
        db.session.commit()
        
        print("Test data created successfully!")

if __name__ == "__main__":
    create_test_data()