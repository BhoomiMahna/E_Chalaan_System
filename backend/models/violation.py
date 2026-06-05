"""
Violation model — SQLAlchemy ORM definition for traffic violations.
Indexed on vehicle_number, date_time, and violation_type for fast filtering.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Violation(db.Model):
    """Represents a single traffic violation record."""
    __tablename__ = 'violations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vehicle_number = db.Column(db.String(30), nullable=False, index=True)
    owner_name = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    violation_type = db.Column(db.String(20), nullable=False, index=True)  # 'no_helmet' or 'red_light'
    fine_amount = db.Column(db.Integer, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    location = db.Column(db.String(100), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, paid, disputed
    image_path = db.Column(db.String(200), nullable=True)
    confidence = db.Column(db.Float, nullable=True)

    def to_dict(self):
        """Serialize violation record to dictionary."""
        return {
            'id': self.id,
            'vehicle_number': self.vehicle_number,
            'owner_name': self.owner_name,
            'address': self.address,
            'violation_type': self.violation_type,
            'fine_amount': self.fine_amount,
            'date_time': self.date_time.isoformat() if self.date_time else None,
            'location': self.location,
            'location_id': self.location_id,
            'status': self.status,
            'image_path': self.image_path,
            'confidence': self.confidence
        }

    def __repr__(self):
        return f'<Violation {self.id}: {self.vehicle_number} - {self.violation_type}>'
