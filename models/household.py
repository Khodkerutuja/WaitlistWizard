from app import db
from models.service import Service, ServiceType

class HouseholdServiceType:
    MAID = 'MAID'
    PLUMBING = 'PLUMBING'
    ELECTRICAL = 'ELECTRICAL'
    PEST_CONTROL = 'PEST_CONTROL'
    CLEANING = 'CLEANING'
    OTHER = 'OTHER'

class HouseholdService(Service):
    __tablename__ = 'household_services'
    
    id = db.Column(db.Integer, db.ForeignKey('services.id'), primary_key=True)
    household_type = db.Column(db.String(20), nullable=False)
    hourly_rate = db.Column(db.Numeric(10, 2), nullable=True)  # For services charged by hour
    visit_charge = db.Column(db.Numeric(10, 2), nullable=True)  # Fixed charge per visit
    estimated_duration = db.Column(db.Integer, nullable=True)   # Duration in minutes
    
    __mapper_args__ = {
        'polymorphic_identity': ServiceType.HOUSEHOLD
    }
    
    def __init__(self, name, description, provider_id, price, household_type, 
                 hourly_rate=None, visit_charge=None, estimated_duration=None, 
                 location=None, availability=None):
        super().__init__(
            name=name, 
            description=description, 
            provider_id=provider_id, 
            service_type=ServiceType.HOUSEHOLD,
            price=price,
            location=location,
            availability=availability
        )
        self.household_type = household_type
        self.hourly_rate = hourly_rate
        self.visit_charge = visit_charge
        self.estimated_duration = estimated_duration
    
    def calculate_total_cost(self, hours=None):
        """Calculate the total cost for the service"""
        # If it's a fixed price service
        if self.price > 0:
            return float(self.price)
        
        # If it's hourly rate service
        if self.hourly_rate and hours:
            total = float(self.hourly_rate) * hours
            if self.visit_charge:
                total += float(self.visit_charge)
            return total
            
        # If it's just a visit charge
        if self.visit_charge:
            return float(self.visit_charge)
            
        # Default case
        return 0
    
    def to_dict(self):
        base_dict = super().to_dict()
        household_dict = {
            'household_type': self.household_type,
            'hourly_rate': float(self.hourly_rate) if self.hourly_rate else None,
            'visit_charge': float(self.visit_charge) if self.visit_charge else None,
            'estimated_duration': self.estimated_duration
        }
        return {**base_dict, **household_dict}
