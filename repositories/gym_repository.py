from models.gym import GymService, GymSubscription
from app import db
from datetime import datetime
import json

class GymRepository:
    def create(self, service):
        """
        Create a new gym service
        
        Args:
            service: GymService object to create
            
        Returns:
            Created service object
        """
        db.session.add(service)
        db.session.commit()
        return service
    
    def update(self, service):
        """
        Update an existing gym service
        
        Args:
            service: GymService object to update
            
        Returns:
            Updated service object
        """
        db.session.commit()
        return service
    
    def delete(self, service):
        """
        Delete a gym service
        
        Args:
            service: GymService object to delete
            
        Returns:
            True if deleted successfully
        """
        db.session.delete(service)
        db.session.commit()
        return True
    
    def find_by_id(self, service_id):
        """
        Find a gym service by ID
        
        Args:
            service_id: ID of the service to find
            
        Returns:
            GymService object if found, None otherwise
        """
        return GymService.query.get(service_id)
    
    def find_all(self, facility_type=None, trainers_available=None, dietician_available=None):
        """
        Find all gym services, optionally filtered
        
        Args:
            facility_type: Filter by facility type (optional)
            trainers_available: Filter by trainer availability (optional)
            dietician_available: Filter by dietician availability (optional)
            
        Returns:
            List of gym service objects
        """
        query = GymService.query
        
        # Filter by trainers/dieticians availability if specified
        if trainers_available is not None:
            query = query.filter_by(trainers_available=trainers_available)
        
        if dietician_available is not None:
            query = query.filter_by(dietician_available=dietician_available)
        
        # Get all services matching the filters
        services = query.all()
        
        # If facility type filter is specified, filter the results
        if facility_type:
            filtered_services = []
            for service in services:
                try:
                    facility_types = json.loads(service.facility_types)
                    if isinstance(facility_types, list) and facility_type.lower() in [ft.lower() for ft in facility_types]:
                        filtered_services.append(service)
                except:
                    # Skip services with invalid facility types
                    pass
            return filtered_services
        
        return services
    
    def create_subscription(self, subscription):
        """
        Create a new gym subscription
        
        Args:
            subscription: GymSubscription object to create
            
        Returns:
            Created subscription object
        """
        db.session.add(subscription)
        db.session.commit()
        return subscription
    
    def update_subscription(self, subscription):
        """
        Update an existing gym subscription
        
        Args:
            subscription: GymSubscription object to update
            
        Returns:
            Updated subscription object
        """
        db.session.commit()
        return subscription
    
    def delete_subscription(self, subscription):
        """
        Delete a gym subscription
        
        Args:
            subscription: GymSubscription object to delete
            
        Returns:
            True if deleted successfully
        """
        db.session.delete(subscription)
        db.session.commit()
        return True
    
    def find_subscription_by_id(self, subscription_id):
        """
        Find a gym subscription by ID
        
        Args:
            subscription_id: ID of the subscription to find
            
        Returns:
            GymSubscription object if found, None otherwise
        """
        return GymSubscription.query.get(subscription_id)
    
    def find_subscriptions_by_user_id(self, user_id, active_only=True):
        """
        Find subscriptions for a user
        
        Args:
            user_id: ID of the user
            active_only: Whether to get only active subscriptions
            
        Returns:
            List of subscription objects
        """
        query = GymSubscription.query.filter_by(user_id=user_id)
        
        if active_only:
            query = query.filter_by(is_active=True)
            query = query.filter(GymSubscription.end_date >= datetime.utcnow())
        
        return query.all()
    
    def find_subscriptions_by_provider_id(self, provider_id, active_only=True):
        """
        Find subscriptions for a service provider
        
        Args:
            provider_id: ID of the service provider
            active_only: Whether to get only active subscriptions
            
        Returns:
            List of subscription objects
        """
        # Get all gym services for the provider
        service_ids = [s.id for s in GymService.query.filter_by(provider_id=provider_id).all()]
        
        # Get subscriptions for these services
        query = GymSubscription.query.filter(GymSubscription.gym_service_id.in_(service_ids))
        
        if active_only:
            query = query.filter_by(is_active=True)
            query = query.filter(GymSubscription.end_date >= datetime.utcnow())
        
        return query.all()
