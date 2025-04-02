from app import db
from models import CarPoolService, ServiceCategory, ServiceStatus
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CarPoolRepository:
    @staticmethod
    def get_by_id(service_id):
        try:
            return CarPoolService.query.get(service_id)
        except SQLAlchemyError as e:
            logger.error(f"Error fetching car pool service by ID: {str(e)}")
            return None
    
    @staticmethod
    def get_all():
        try:
            return CarPoolService.query.filter_by(
                status=ServiceStatus.AVAILABLE
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all car pool services: {str(e)}")
            return []
    
    @staticmethod
    def get_by_provider(provider_id):
        try:
            return CarPoolService.query.filter_by(provider_id=provider_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching car pool services by provider: {str(e)}")
            return []
    
    @staticmethod
    def get_available_rides(source, destination, departure_date):
        try:
            # Get rides with available seats for the given source, destination, and date
            departure_date = datetime.strptime(departure_date, '%Y-%m-%d')
            next_day = departure_date.replace(hour=23, minute=59, second=59)
            departure_date = departure_date.replace(hour=0, minute=0, second=0)
            
            return CarPoolService.query.filter(
                CarPoolService.source.ilike(f'%{source}%'),
                CarPoolService.destination.ilike(f'%{destination}%'),
                CarPoolService.departure_time.between(departure_date, next_day),
                CarPoolService.available_seats > 0,
                CarPoolService.status == ServiceStatus.AVAILABLE
            ).all()
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f"Error fetching available rides: {str(e)}")
            return []
    
    @staticmethod
    def create(data, provider_id):
        try:
            car_pool_service = CarPoolService(
                name=data['name'],
                description=data['description'],
                category=ServiceCategory.CAR_POOL if data['vehicle_type'].lower() == 'car' else ServiceCategory.BIKE_POOL,
                price=data['price'],
                provider_id=provider_id,
                status=ServiceStatus.AVAILABLE,
                vehicle_type=data['vehicle_type'],
                vehicle_model=data.get('vehicle_model', ''),
                capacity=data['capacity'],
                available_seats=data['available_seats'],
                source=data['source'],
                destination=data['destination'],
                departure_time=data['departure_time']
            )
            db.session.add(car_pool_service)
            db.session.commit()
            return car_pool_service
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error creating car pool service: {str(e)}")
            return None
    
    @staticmethod
    def update(service, data):
        try:
            for key, value in data.items():
                setattr(service, key, value)
            
            db.session.commit()
            return service
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating car pool service: {str(e)}")
            return None
    
    @staticmethod
    def update_available_seats(service, seats_to_decrease=1):
        try:
            if service.available_seats >= seats_to_decrease:
                service.available_seats -= seats_to_decrease
                
                # If no more seats, mark as unavailable
                if service.available_seats == 0:
                    service.status = ServiceStatus.UNAVAILABLE
                
                db.session.commit()
                return service
            else:
                raise ValueError("Not enough available seats")
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            logger.error(f"Error updating available seats: {str(e)}")
            return None
    
    @staticmethod
    def cancel_booking(service, seats_to_increase=1):
        try:
            service.available_seats += seats_to_increase
            
            # If service was unavailable due to full capacity, mark as available again
            if service.status == ServiceStatus.UNAVAILABLE and service.available_seats > 0:
                service.status = ServiceStatus.AVAILABLE
            
            db.session.commit()
            return service
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error canceling booking: {str(e)}")
            return None
