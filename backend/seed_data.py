"""
Seed Data Script — Populates the database with 250+ realistic demo violations.
Run: python seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.violation import db, Violation
from cv_module.simulator import ViolationSimulator


def seed_database(count=250):
    """Generate and insert demo violation records."""
    app = create_app()

    with app.app_context():
        # Check if data already exists
        existing = Violation.query.count()
        if existing > 0:
            print(f"Database already has {existing} records.")
            response = input("Clear and re-seed? (y/n): ").strip().lower()
            if response != 'y':
                print("Skipping seed.")
                return
            Violation.query.delete()
            db.session.commit()
            print("Cleared existing data.")

        # Generate violations
        print(f"Generating {count} violation records...")
        violations = ViolationSimulator.generate_violations(count)

        for v_data in violations:
            violation = Violation(
                vehicle_number=v_data['vehicle_number'],
                owner_name=v_data['owner_name'],
                address=v_data['address'],
                violation_type=v_data['violation_type'],
                fine_amount=v_data['fine_amount'],
                date_time=v_data['date_time'],
                location=v_data['location'],
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
