from app import db
from models.service import Service, ServiceType

class MechanicalServiceType:
    BIKE_REPAIR = 'BIKE_REPAIR'
    CAR_REPAIR = 'CAR_REPAIR'
    GENERAL_MAINTENANCE = 'GENERAL_MAINTENANCE'
    BREAKDOWN_ASSISTANCE = 'BREAKDOWN_ASSISTANCE'
    TOWING = 'TOWING'
    OTHER = 'OTHER'

class MechanicalService(Service):
    __tablename__ = 'mechanical_services'
    
    id = db.Column(db.Integer, db.ForeignKey('services.id'), primary_key=True)
    mechanical_type = db.Column(db.String(30), nullable=False)
    service_charge = db.Column(db.Numeric(10, 2), nullable=False)  # Fixed service charge
    additional_charges_desc = db.Column(db.Text, nullable=True)    # Description of additional charges
    estimated_time = db.Column(db.Integer, nullable=True)         # Estimated time in minutes
    offers_pickup = db.Column(db.Boolean, default=False)          # Whether pickup service is available
    pickup_charge = db.Column(db.Numeric(10, 2), nullable=True)   # Charge for pickup service
    
    __mapper_args__ = {
        'polymorphic_identity': ServiceType.MECHANICAL
    }
    
    def __init__(self, name, description, provider_id, service_charge, mechanical_type, 
                 additional_charges_desc=None, estimated_time=None, offers_pickup=False, 
                 pickup_charge=None, location=None, availability=None):
        super().__init__(
            name=name, 
            description=description, 
            provider_id=provider_id, 
            service_type=ServiceType.MECHANICAL,
            price=service_charge,  # The base price is the service charge
            location=location,
            availability=availability
        )
        self.mechanical_type = mechanical_type
        self.service_charge = service_charge
        self.additional_charges_desc = additional_charges_desc
        self.estimated_time = estimated_time
        self.offers_pickup = offers_pickup
        self.pickup_charge = pickup_charge
    
    def get_total_charge(self, include_pickup=False):
        """Get the total charge including pickup if requested"""
        total = float(self.service_charge)
        if include_pickup and self.offers_pickup and self.pickup_charge:
            total += float(self.pickup_charge)
        return total
    
    def to_dict(self):
        base_dict = super().to_dict()
        mechanical_dict = {
            'mechanical_type': self.mechanical_type,
            'service_charge': float(self.service_charge),
            'additional_charges_desc': self.additional_charges_desc,
            'estimated_time': self.estimated_time,
            'offers_pickup': self.offers_pickup,
            'pickup_charge': float(self.pickup_charge) if self.pickup_charge else None
        }
        return {**base_dict, **mechanical_dict}
