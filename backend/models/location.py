from .violation import db

class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    area_code = db.Column(db.String(20), nullable=True)
    camera_id = db.Column(db.String(50), nullable=True)

    violations = db.relationship('Violation', backref='location_rel', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'area_code': self.area_code,
            'camera_id': self.camera_id
        }
