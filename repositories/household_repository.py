from models.household import HouseholdService
from app import db

class HouseholdRepository:
    def create(self, service):
        """
        Create a new household service
        
        Args:
            service: HouseholdService object to create
            
        Returns:
            Created service object
        """
        db.session.add(service)
        db.session.commit()
        return service
    
    def update(self, service):
        """
        Update an existing household service
        
        Args:
            service: HouseholdService object to update
            
        Returns:
            Updated service object
        """
        db.session.commit()
        return service
    
    def delete(self, service):
        """
        Delete a household service
        
        Args:
            service: HouseholdService object to delete
            
        Returns:
            True if deleted successfully
        """
        db.session.delete(service)
        db.session.commit()
        return True
    
    def find_by_id(self, service_id):
        """
        Find a household service by ID
        
        Args:
            service_id: ID of the service to find
            
        Returns:
            HouseholdService object if found, None otherwise
        """
        return HouseholdService.query.get(service_id)
    
    def find_all(self, household_type=None, location=None):
        """
        Find all household services, optionally filtered
        
        Args:
            household_type: Filter by household service type (optional)
            location: Filter by location (optional)
            
        Returns:
            List of household service objects
        """
        query = HouseholdService.query
        
        if household_type:
            query = query.filter_by(household_type=household_type)
        
        if location:
            query = query.filter(HouseholdService.location.ilike(f"%{location}%"))
        
        return query.all()
