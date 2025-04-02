from datetime import datetime, timedelta
from models.gym import GymService, GymSubscription, SubscriptionPlan
from models.service import ServiceType
from repositories.gym_repository import GymRepository
from services.wallet_service import WalletService
from app import db
import json

class GymService:
    def __init__(self):
        self.gym_repository = GymRepository()
        self.wallet_service = WalletService()
    
    def get_gym_services(self, facility_type=None, trainers_available=None, dietician_available=None):
        """
        Get gym services, optionally filtered
        
        Args:
            facility_type: Filter by facility type (optional)
            trainers_available: Filter by trainer availability (optional)
            dietician_available: Filter by dietician availability (optional)
            
        Returns:
            List of gym service objects
        """
        return self.gym_repository.find_all(
            facility_type=facility_type,
            trainers_available=trainers_available,
            dietician_available=dietician_available
        )
    
    def create_gym_service(self, name, description, provider_id, gym_name, facility_types,
                          operating_hours, subscription_plans, trainers_available=False,
                          dietician_available=False, location=None):
        """
        Create a new gym service
        
        Args:
            name: Service name
            description: Service description
            provider_id: ID of the service provider
            gym_name: Name of the gym
            facility_types: List of facility types available
            operating_hours: Dictionary of operating hours
            subscription_plans: Dictionary of subscription plans and prices
            trainers_available: Whether trainers are available
            dietician_available: Whether dieticians are available
            location: Service location (optional)
            
        Returns:
            Newly created gym service object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        if not gym_name or not facility_types or not operating_hours or not subscription_plans:
            raise ValueError("Gym name, facility types, operating hours, and subscription plans are required")
        
        # Validate subscription plans
        if not isinstance(subscription_plans, dict) and not isinstance(subscription_plans, str):
            raise ValueError("Subscription plans must be a dictionary or JSON string")
        
        if isinstance(subscription_plans, dict):
            for plan in [SubscriptionPlan.MONTHLY, SubscriptionPlan.QUARTERLY, SubscriptionPlan.ANNUAL]:
                if plan not in subscription_plans:
                    raise ValueError(f"Subscription plan {plan} is required")
        
        # Create gym service
        service = GymService(
            name=name,
            description=description,
            provider_id=provider_id,
            gym_name=gym_name,
            facility_types=facility_types,
            operating_hours=operating_hours,
            subscription_plans=subscription_plans,
            trainers_available=trainers_available,
            dietician_available=dietician_available
        )
        
        # Set location
        if location:
            service.location = location
        
        # Save service
        return self.gym_repository.create(service)
    
    def update_gym_service(self, service_id, provider_id, data):
        """
        Update a gym service
        
        Args:
            service_id: ID of the service to update
            provider_id: ID of the service provider (for authorization)
            data: Dictionary of fields to update
            
        Returns:
            Updated gym service object
            
        Raises:
            ValueError: If service not found or provider not authorized
        """
        # Get service
        service = self.gym_repository.find_by_id(service_id)
        if not service:
            raise ValueError(f"Gym service with ID {service_id} not found")
        
        # Check if provider is authorized
        if service.provider_id != provider_id:
            raise ValueError("Not authorized to update this service")
        
        # Update base service fields
        if 'name' in data:
            service.name = data['name']
        if 'description' in data:
            service.description = data['description']
        
        # Update gym specific fields
        if 'gym_name' in data:
            service.gym_name = data['gym_name']
        if 'facility_types' in data:
            service.facility_types = json.dumps(data['facility_types']) if isinstance(data['facility_types'], list) else data['facility_types']
        if 'operating_hours' in data:
            service.operating_hours = json.dumps(data['operating_hours']) if isinstance(data['operating_hours'], dict) else data['operating_hours']
        if 'subscription_plans' in data:
            # Validate subscription plans
            subscription_plans = data['subscription_plans']
            if isinstance(subscription_plans, dict):
                for plan in [SubscriptionPlan.MONTHLY, SubscriptionPlan.QUARTERLY, SubscriptionPlan.ANNUAL]:
                    if plan not in subscription_plans:
                        raise ValueError(f"Subscription plan {plan} is required")
                service.subscription_plans = json.dumps(subscription_plans)
            elif isinstance(subscription_plans, str):
                service.subscription_plans = subscription_plans
            else:
                raise ValueError("Subscription plans must be a dictionary or JSON string")
        if 'trainers_available' in data:
            service.trainers_available = data['trainers_available']
        if 'dietician_available' in data:
            service.dietician_available = data['dietician_available']
        if 'location' in data:
            service.location = data['location']
        
        # Save updated service
        return self.gym_repository.update(service)
    
    def subscribe_to_gym(self, user_id, service_id, subscription_plan, trainer_required=False, dietician_required=False):
        """
        Subscribe to a gym service
        
        Args:
            user_id: ID of the user subscribing
            service_id: ID of the gym service
            subscription_plan: Type of subscription plan
            trainer_required: Whether a trainer is required
            dietician_required: Whether a dietician is required
            
        Returns:
            Newly created gym subscription object
            
        Raises:
            ValueError: If service not found, invalid subscription plan, or other validation fails
        """
        # Get service
        service = self.gym_repository.find_by_id(service_id)
        if not service:
            raise ValueError(f"Gym service with ID {service_id} not found")
        
        # Validate subscription plan
        if subscription_plan not in [SubscriptionPlan.MONTHLY, SubscriptionPlan.QUARTERLY, SubscriptionPlan.ANNUAL]:
            raise ValueError(f"Invalid subscription plan: {subscription_plan}")
        
        # Get subscription price
        subscription_plans = service.get_subscription_plans()
        price = subscription_plans.get(subscription_plan)
        if not price:
            raise ValueError(f"Price not found for subscription plan: {subscription_plan}")
        
        # Check if trainer/dietician required but not available
        if trainer_required and not service.trainers_available:
            raise ValueError("Trainers are not available at this gym")
        if dietician_required and not service.dietician_available:
            raise ValueError("Dieticians are not available at this gym")
        
        # Calculate subscription period
        start_date = datetime.utcnow()
        if subscription_plan == SubscriptionPlan.MONTHLY:
            end_date = start_date + timedelta(days=30)
        elif subscription_plan == SubscriptionPlan.QUARTERLY:
            end_date = start_date + timedelta(days=90)
        elif subscription_plan == SubscriptionPlan.ANNUAL:
            end_date = start_date + timedelta(days=365)
        
        # Verify wallet has sufficient funds
        wallet = self.wallet_service.get_wallet_by_user_id(user_id)
        if not wallet or not wallet.has_sufficient_funds(price):
            raise ValueError("Insufficient funds in wallet")
        
        try:
            # Process payment
            payment_success = self.wallet_service.transfer_payment(
                from_user_id=user_id,
                to_user_id=service.provider_id,
                amount=price,
                reference_id=f"gym_subscription_{user_id}_{service_id}_{datetime.utcnow().timestamp()}"
            )
            
            if not payment_success:
                raise ValueError("Payment processing failed")
            
            # Create subscription
            subscription = GymSubscription(
                user_id=user_id,
                gym_service_id=service_id,
                subscription_plan=subscription_plan,
                start_date=start_date,
                end_date=end_date,
                amount_paid=price,
                trainer_assigned="TBD" if trainer_required else None,
                dietician_assigned="TBD" if dietician_required else None
            )
            
            # Save subscription
            return self.gym_repository.create_subscription(subscription)
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_user_subscriptions(self, user_id, active_only=True):
        """
        Get subscriptions for a user
        
        Args:
            user_id: ID of the user
            active_only: Whether to get only active subscriptions
            
        Returns:
            List of subscription objects
        """
        return self.gym_repository.find_subscriptions_by_user_id(user_id, active_only)
    
    def get_provider_subscriptions(self, provider_id, active_only=True):
        """
        Get subscriptions for a service provider
        
        Args:
            provider_id: ID of the service provider
            active_only: Whether to get only active subscriptions
            
        Returns:
            List of subscription objects
        """
        return self.gym_repository.find_subscriptions_by_provider_id(provider_id, active_only)
    
    def update_subscription(self, subscription_id, data):
        """
        Update a gym subscription
        
        Args:
            subscription_id: ID of the subscription to update
            data: Dictionary of fields to update
            
        Returns:
            Updated subscription object
            
        Raises:
            ValueError: If subscription not found
        """
        # Get subscription
        subscription = self.gym_repository.find_subscription_by_id(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription with ID {subscription_id} not found")
        
        # Update fields
        if 'trainer_assigned' in data:
            subscription.trainer_assigned = data['trainer_assigned']
        if 'dietician_assigned' in data:
            subscription.dietician_assigned = data['dietician_assigned']
        if 'is_active' in data:
            subscription.is_active = data['is_active']
        
        # Save updated subscription
        return self.gym_repository.update_subscription(subscription)
