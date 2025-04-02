from models.car_pool import CarPoolService
from app import db
from datetime import datetime

class CarPoolRepository:
    def create(self, service):
        """
        Create a new car pool service
        
        Args:
            service: CarPoolService object to create
            
        Returns:
            Created service object
        """
        db.session.add(service)
        db.session.commit()
        return service
    
    def update(self, service):
        """
        Update an existing car pool service
        
        Args:
            service: CarPoolService object to update
            
        Returns:
            Updated service object
        """
        db.session.commit()
        return service
    
    def delete(self, service):
        """
        Delete a car pool service
        
        Args:
            service: CarPoolService object to delete
            
        Returns:
            True if deleted successfully
        """
        db.session.delete(service)
        db.session.commit()
        return True
    
    def find_by_id(self, service_id):
        """
        Find a car pool service by ID
        
        Args:
            service_id: ID of the service to find
            
        Returns:
            CarPoolService object if found, None otherwise
        """
        return CarPoolService.query.get(service_id)
    
    def find_all(self, vehicle_type=None, source=None, destination=None, date=None):
        """
        Find all car pool services, optionally filtered
        
        Args:
            vehicle_type: Filter by vehicle type (optional)
            source: Filter by source location (optional)
            destination: Filter by destination (optional)
            date: Filter by departure date (optional)
            
        Returns:
            List of car pool service objects
        """
        query = CarPoolService.query
        
        if vehicle_type:
            query = query.filter_by(vehicle_type=vehicle_type)
        
        if source:
            query = query.filter(CarPoolService.source.ilike(f"%{source}%"))
        
        if destination:
            query = query.filter(CarPoolService.destination.ilike(f"%{destination}%"))
        
        if date:
            # Convert date string to datetime
            if isinstance(date, str):
                try:
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    # Filter for services on this date
                    query = query.filter(
                        db.func.date(CarPoolService.departure_time) == date_obj.date()
                    )
                except ValueError:
                    # Invalid date format, ignore this filter
                    pass
        
        # Only show services with available seats
        query = query.filter(CarPoolService.available_seats > 0)
        
        # Filter out services with departure time in the past
        query = query.filter(CarPoolService.departure_time > datetime.utcnow())
        
        # Order by departure time
        query = query.order_by(CarPoolService.departure_time)
        
        return query.all()
