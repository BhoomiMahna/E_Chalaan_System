"""
Seed Data Script — Populates the database with 250+ realistic demo violations.
Run: python seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.violation import db, Violation
from models.location import Location
from models.violation_fine import ViolationFine
from cv_module.simulator import ViolationSimulator
from datetime import datetime


def seed_database(count=250):
    """Generate and insert demo violation records."""
    app = create_app()

    with app.app_context():
        # Clear existing data safely
        Violation.query.delete()
        Location.query.delete()
        ViolationFine.query.delete()
        db.session.commit()
        print("Cleared existing data.")

        # Seed Locations
        locations_data = [
            {"name": "MG Road, Sector 17", "latitude": 30.7333, "longitude": 76.7794, "area_code": "SEC17"},
            {"name": "NH-44, Panipat Bypass", "latitude": 29.3909, "longitude": 76.9635, "area_code": "PNP44"},
            {"name": "GT Road, Ludhiana", "latitude": 30.9010, "longitude": 75.8573, "area_code": "LDHGT"},
            {"name": "Rajpura Chowk, Patiala", "latitude": 30.3398, "longitude": 76.3869, "area_code": "PTLRJ"},
            {"name": "Bus Stand, Jalandhar", "latitude": 31.3260, "longitude": 75.5762, "area_code": "JALBS"},
            {"name": "Mall Road, Shimla", "latitude": 31.1048, "longitude": 77.1734, "area_code": "SHMML"},
            {"name": "Ferozepur Road, Ludhiana", "latitude": 30.8986, "longitude": 75.8239, "area_code": "LDHFZ"},
            {"name": "Chandigarh-Ambala Highway", "latitude": 30.5510, "longitude": 76.8173, "area_code": "CHAMB"},
            {"name": "Civil Lines, Amritsar", "latitude": 31.6340, "longitude": 74.8723, "area_code": "ASRCL"},
            {"name": "Model Town, Karnal", "latitude": 29.6857, "longitude": 76.9905, "area_code": "KRNMT"},
        ]
        
        db_locations = []
        for loc_data in locations_data:
            loc = Location(**loc_data)
            db.session.add(loc)
            db_locations.append(loc)
        db.session.commit()
        print(f"Seeded {len(db_locations)} locations.")

        # Seed Violation Fines
        fines_data = [
            {"violation_type": "no_helmet", "base_amount": 1000},
            {"violation_type": "red_light", "base_amount": 5000}
        ]
        for fine in fines_data:
            db.session.add(ViolationFine(**fine))
        db.session.commit()
        print(f"Seeded {len(fines_data)} violation fines.")

        # Generate violations
        print(f"Generating {count} violation records...")
        violations = ViolationSimulator.generate_violations(count)

        for v_data in violations:
            # Map location string to location_id
            loc_obj = next((l for l in db_locations if l.name == v_data['location']), db_locations[0])
            
            violation = Violation(
                vehicle_number=v_data['vehicle_number'],
                owner_name=v_data['owner_name'],
                address=v_data['address'],
                violation_type=v_data['violation_type'],
                fine_amount=v_data['fine_amount'],
                date_time=v_data['date_time'],
                location=loc_obj.name,
                location_id=loc_obj.id,
                status=v_data['status'],
                image_path=v_data['image_path'],
                confidence=v_data['confidence']
            )
            db.session.add(violation)

        db.session.commit()
        print(f"Successfully seeded {count} violation records!")

        # Print summary
        total = Violation.query.count()
        helmet = Violation.query.filter_by(violation_type='no_helmet').count()
        red = Violation.query.filter_by(violation_type='red_light').count()
        print(f"\nSummary:")
        print(f"  Total violations: {total}")
        print(f"  Helmet violations: {helmet}")
        print(f"  Red-light violations: {red}")


if __name__ == '__main__':
    seed_database()
