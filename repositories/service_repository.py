from models.service import Service, ServiceStatus
from app import db
from sqlalchemy import or_, and_

class ServiceRepository:
    def create(self, service):
        """
        Create a new service
        
        Args:
            service: Service object to create
            
        Returns:
            Created service object
        """
        db.session.add(service)
        db.session.commit()
        return service
    
    def update(self, service):
        """
        Update an existing service
        
        Args:
            service: Service object to update
            
        Returns:
            Updated service object
        """
        db.session.commit()
        return service
    
    def delete(self, service):
        """
        Delete a service
        
        Args:
            service: Service object to delete
            
        Returns:
            True if deleted successfully
        """
        db.session.delete(service)
        db.session.commit()
        return True
    
    def find_by_id(self, service_id):
        """
        Find a service by ID
        
        Args:
            service_id: ID of the service to find
            
        Returns:
            Service object if found, None otherwise
        """
        return Service.query.get(service_id)
    
    def find_all(self, service_type=None, status=None, provider_id=None):
        """
        Find all services, optionally filtered by type, status, and/or provider
        
        Args:
            service_type: Filter by service type (optional)
            status: Filter by status (optional)
            provider_id: Filter by provider ID (optional)
            
        Returns:
            List of service objects
        """
        query = Service.query
        
        if service_type:
            query = query.filter_by(service_type=service_type)
        
        if status:
            query = query.filter_by(status=status)
        
        if provider_id:
            query = query.filter_by(provider_id=provider_id)
        
        # Don't return deleted services unless explicitly requested
        if status != ServiceStatus.DELETED:
            query = query.filter(Service.status != ServiceStatus.DELETED)
        
        return query.all()
    
    def search(self, search_term, service_type=None, status=None):
        """
        Search for services by name or description
        
        Args:
            search_term: Term to search for
            service_type: Filter by service type (optional)
            status: Filter by status (optional)
            
        Returns:
            List of service objects matching the search
        """
        query = Service.query.filter(
            or_(
                Service.name.ilike(f"%{search_term}%"),
                Service.description.ilike(f"%{search_term}%")
            )
        )
        
        if service_type:
            query = query.filter_by(service_type=service_type)
        
        if status:
            query = query.filter_by(status=status)
        else:
            query = query.filter(Service.status != ServiceStatus.DELETED)
        
        return query.all()
    
    def count_all(self, status=None):
        """
        Count all services, optionally filtered by status
        
        Args:
            status: Filter by status (optional)
            
        Returns:
            Number of services
        """
        query = Service.query
        
        if status:
            query = query.filter_by(status=status)
        else:
            query = query.filter(Service.status != ServiceStatus.DELETED)
        
        return query.count()
