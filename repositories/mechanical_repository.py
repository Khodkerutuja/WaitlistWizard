from models.mechanical import MechanicalService
from app import db

class MechanicalRepository:
    def create(self, service):
        """
        Create a new mechanical service
        
        Args:
            service: MechanicalService object to create
            
        Returns:
            Created service object
        """
        db.session.add(service)
        db.session.commit()
        return service
    
    def update(self, service):
        """
        Update an existing mechanical service
        
        Args:
            service: MechanicalService object to update
            
        Returns:
            Updated service object
        """
        db.session.commit()
        return service
    
    def delete(self, service):
        """
        Delete a mechanical service
        
        Args:
            service: MechanicalService object to delete
            
        Returns:
            True if deleted successfully
        """
        db.session.delete(service)
        db.session.commit()
        return True
    
    def find_by_id(self, service_id):
        """
        Find a mechanical service by ID
        
        Args:
            service_id: ID of the service to find
            
        Returns:
            MechanicalService object if found, None otherwise
        """
        return MechanicalService.query.get(service_id)
    
    def find_all(self, mechanical_type=None, offers_pickup=None, location=None):
        """
        Find all mechanical services, optionally filtered
        
        Args:
            mechanical_type: Filter by mechanical service type (optional)
            offers_pickup: Filter by pickup service availability (optional)
            location: Filter by location (optional)
            
        Returns:
            List of mechanical service objects
        """
        query = MechanicalService.query
        
        if mechanical_type:
            query = query.filter_by(mechanical_type=mechanical_type)
        
        if offers_pickup is not None:
            query = query.filter_by(offers_pickup=offers_pickup)
        
        if location:
            query = query.filter(MechanicalService.location.ilike(f"%{location}%"))
        
        return query.all()
