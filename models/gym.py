from app import db
from models.service import Service, ServiceType
import json

class SubscriptionPlan:
    MONTHLY = 'MONTHLY'
    QUARTERLY = 'QUARTERLY'
    ANNUAL = 'ANNUAL'

class GymService(Service):
    __tablename__ = 'gym_services'
    
    id = db.Column(db.Integer, db.ForeignKey('services.id'), primary_key=True)
    gym_name = db.Column(db.String(100), nullable=False)
    facility_types = db.Column(db.String(255), nullable=False)  # JSON string: ["yoga", "weightlifting", ...]
    operating_hours = db.Column(db.String(255), nullable=False)  # JSON string
    trainers_available = db.Column(db.Boolean, default=False)
    dietician_available = db.Column(db.Boolean, default=False)
    
    # Subscription plans as JSON: {"MONTHLY": 2000, "QUARTERLY": 5500, "ANNUAL": 20000}
    subscription_plans = db.Column(db.String(255), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': ServiceType.GYM_FITNESS
    }
    
    def __init__(self, name, description, provider_id, gym_name, facility_types, 
                 operating_hours, subscription_plans, trainers_available=False, 
                 dietician_available=False):
        super().__init__(
            name=name, 
            description=description, 
            provider_id=provider_id, 
            service_type=ServiceType.GYM_FITNESS,
            price=0  # Base price, actual price depends on subscription plan
        )
        self.gym_name = gym_name
        self.facility_types = json.dumps(facility_types) if isinstance(facility_types, list) else facility_types
        self.operating_hours = json.dumps(operating_hours) if isinstance(operating_hours, dict) else operating_hours
        self.subscription_plans = json.dumps(subscription_plans) if isinstance(subscription_plans, dict) else subscription_plans
        self.trainers_available = trainers_available
        self.dietician_available = dietician_available
    
    def get_facility_types(self):
        """Get the facility types as a list"""
        return json.loads(self.facility_types)
    
    def get_operating_hours(self):
        """Get the operating hours as a dictionary"""
        return json.loads(self.operating_hours)
    
    def get_subscription_plans(self):
        """Get the subscription plans as a dictionary"""
        return json.loads(self.subscription_plans)
    
    def get_price_for_plan(self, plan):
        """Get the price for a specific subscription plan"""
        plans = self.get_subscription_plans()
        if plan not in plans:
            raise ValueError(f"Invalid subscription plan: {plan}")
        return plans[plan]
    
    def to_dict(self):
        base_dict = super().to_dict()
        gym_dict = {
            'gym_name': self.gym_name,
            'facility_types': self.get_facility_types(),
            'operating_hours': self.get_operating_hours(),
            'trainers_available': self.trainers_available,
            'dietician_available': self.dietician_available,
            'subscription_plans': self.get_subscription_plans()
        }
        return {**base_dict, **gym_dict}

class GymSubscription(db.Model):
    __tablename__ = 'gym_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    gym_service_id = db.Column(db.Integer, db.ForeignKey('gym_services.id'), nullable=False)
    subscription_plan = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    amount_paid = db.Column(db.Numeric(10, 2), nullable=False)
    trainer_assigned = db.Column(db.String(100), nullable=True)
    dietician_assigned = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref='gym_subscriptions')
    gym_service = db.relationship('GymService', backref='subscriptions')
    
    def __init__(self, user_id, gym_service_id, subscription_plan, start_date, end_date, 
                 amount_paid, trainer_assigned=None, dietician_assigned=None):
        self.user_id = user_id
        self.gym_service_id = gym_service_id
        self.subscription_plan = subscription_plan
        self.start_date = start_date
        self.end_date = end_date
        self.amount_paid = amount_paid
        self.trainer_assigned = trainer_assigned
        self.dietician_assigned = dietician_assigned
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'gym_service_id': self.gym_service_id,
            'subscription_plan': self.subscription_plan,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'amount_paid': float(self.amount_paid),
            'trainer_assigned': self.trainer_assigned,
            'dietician_assigned': self.dietician_assigned,
            'is_active': self.is_active
        }
