from .violation import db
from datetime import datetime

class ViolationFine(db.Model):
    __tablename__ = 'violation_fines'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    violation_type = db.Column(db.String(50), nullable=False, index=True)
    base_amount = db.Column(db.Integer, nullable=False)
    effective_from = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    effective_to = db.Column(db.DateTime, nullable=True)
    area_id = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'violation_type': self.violation_type,
            'base_amount': self.base_amount,
            'effective_from': self.effective_from.isoformat() if self.effective_from else None,
            'effective_to': self.effective_to.isoformat() if self.effective_to else None,
            'area_id': self.area_id
        }
