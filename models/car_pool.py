from app import db
from models.service import Service
from models.enum_types import ServiceType, VehicleType
import json

class CarPoolService(Service):
    __tablename__ = 'car_pool_services'
    
    id = db.Column(db.Integer, db.ForeignKey('services.id'), primary_key=True)
    vehicle_type = db.Column(db.String(10), nullable=False)
    source = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    vehicle_model = db.Column(db.String(100), nullable=True)
    vehicle_number = db.Column(db.String(20), nullable=True)
    
    __mapper_args__ = {
        'polymorphic_identity': ServiceType.CAR_POOL
    }
    
    def __init__(self, name, description, provider_id, price, vehicle_type, source, destination, 
                 departure_time, total_seats, vehicle_model=None, vehicle_number=None):
        super().__init__(
            name=name, 
            description=description, 
            provider_id=provider_id, 
            service_type=ServiceType.CAR_POOL,
            price=price
        )
        self.vehicle_type = vehicle_type
        self.source = source
        self.destination = destination
        self.departure_time = departure_time
        self.total_seats = total_seats
        self.available_seats = total_seats  # Initially, all seats are available
        self.vehicle_model = vehicle_model
        self.vehicle_number = vehicle_number
    
    def book_seat(self, num_seats=1):
        """Book a seat in the car/bike pool"""
        if num_seats <= 0:
            raise ValueError("Number of seats must be positive")
        if self.available_seats < num_seats:
            raise ValueError(f"Only {self.available_seats} seats available")
        self.available_seats -= num_seats
    
    def release_seat(self, num_seats=1):
        """Release a previously booked seat"""
        if num_seats <= 0:
            raise ValueError("Number of seats must be positive")
        if self.available_seats + num_seats > self.total_seats:
            raise ValueError(f"Cannot release more than total seats ({self.total_seats})")
        self.available_seats += num_seats
    
    def is_fully_booked(self):
        """Check if the car/bike pool is fully booked"""
        return self.available_seats == 0
    
    def to_dict(self):
        base_dict = super().to_dict()
        car_pool_dict = {
            'vehicle_type': self.vehicle_type,
            'source': self.source,
            'destination': self.destination,
            'departure_time': self.departure_time.isoformat() if self.departure_time else None,
            'total_seats': self.total_seats,
            'available_seats': self.available_seats,
            'vehicle_model': self.vehicle_model,
            'vehicle_number': self.vehicle_number
        }
        return {**base_dict, **car_pool_dict}

class BikePoolService(CarPoolService):
    __mapper_args__ = {
        'polymorphic_identity': ServiceType.BIKE_POOL
    }
    
    def __init__(self, name, description, provider_id, price, source, destination, 
                 departure_time, total_seats, vehicle_model=None, vehicle_number=None):
        super().__init__(
            name=name, 
            description=description, 
            provider_id=provider_id,
            price=price,
            vehicle_type=VehicleType.BIKE,
            source=source,
            destination=destination,
            departure_time=departure_time,
            total_seats=total_seats,
            vehicle_model=vehicle_model,
            vehicle_number=vehicle_number
        )
        # Override service_type
        self.service_type = ServiceType.BIKE_POOL
