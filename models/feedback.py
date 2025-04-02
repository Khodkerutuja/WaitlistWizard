from datetime import datetime
from app import db

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, provider_id, service_id, rating, review=None):
        self.user_id = user_id
        self.provider_id = provider_id
        self.service_id = service_id
        self.rating = rating
        self.review = review
    
    @staticmethod
    def get_average_rating(provider_id):
        """Get the average rating for a provider"""
        from sqlalchemy import func
        result = db.session.query(func.avg(Feedback.rating)).filter_by(provider_id=provider_id).scalar()
        return float(result) if result else 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'provider_id': self.provider_id,
            'service_id': self.service_id,
            'rating': self.rating,
            'review': self.review,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
