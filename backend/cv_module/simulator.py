"""
Simulator — Generates realistic demo violation data for testing.
Creates random Indian-format plates, names, addresses, and violations
spread across the last 30 days.
"""
import random
from datetime import datetime, timedelta


class ViolationSimulator:
    """Generates realistic demo violation records."""

    STATES = ['DL', 'HR', 'PB', 'UP', 'MH', 'KA', 'TN', 'RJ', 'GJ', 'MP']
    FIRST_NAMES = [
        'Rajesh', 'Amit', 'Priya', 'Sunita', 'Vikram', 'Deepak', 'Anita',
        'Suresh', 'Kavita', 'Rahul', 'Pooja', 'Manish', 'Neha', 'Arun',
        'Sanjay', 'Ritu', 'Vijay', 'Meera', 'Ankur', 'Divya', 'Harsh',
        'Simran', 'Rohit', 'Nisha', 'Karan', 'Swati', 'Gaurav', 'Preeti'
    ]
    LAST_NAMES = [
        'Kumar', 'Sharma', 'Singh', 'Verma', 'Gupta', 'Jain', 'Patel',
        'Rao', 'Reddy', 'Mishra', 'Chopra', 'Malhotra', 'Kapoor', 'Mehta',
        'Chauhan', 'Thakur', 'Bansal', 'Arora', 'Bhatia', 'Khanna'
    ]
    STREETS = [
        'Model Town', 'Civil Lines', 'Sector 17', 'MG Road', 'Rajpur Road',
        'Mall Road', 'GT Road', 'Ring Road', 'Station Road', 'College Road',
        'Market Street', 'Gandhi Nagar', 'Nehru Colony', 'Lajpat Nagar'
    ]
    CITIES = [
        'Chandigarh', 'Ludhiana', 'Amritsar', 'Jalandhar', 'Shimla',
        'Dehradun', 'Jaipur', 'Delhi', 'Karnal', 'Panipat', 'Ambala', 'Patiala'
    ]
    LOCATIONS = [
        'MG Road, Sector 17', 'NH-44, Panipat Bypass', 'GT Road, Ludhiana',
        'Rajpura Chowk, Patiala', 'Bus Stand, Jalandhar', 'Mall Road, Shimla',
        'Ferozepur Road, Ludhiana', 'Chandigarh-Ambala Highway',
        'Civil Lines, Amritsar', 'Model Town, Karnal', 'Sector 22, Chandigarh',
        'Industrial Area Phase 1, Chandigarh', 'GT Road, Panipat',
        'Lawrence Road, Amritsar', 'Rajpura Road, Patiala'
    ]

    @classmethod
    def generate_plate(cls):
        """Generate a random Indian-format license plate."""
        state = random.choice(cls.STATES)
        district = random.randint(1, 99)
        letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
        number = random.randint(1000, 9999)
        return f"{state}{district:02d}{letters}{number}"

    @classmethod
    def generate_name(cls):
        return f"{random.choice(cls.FIRST_NAMES)} {random.choice(cls.LAST_NAMES)}"

    @classmethod
    def generate_address(cls):
        return f"{random.randint(1, 500)}, {random.choice(cls.STREETS)}, {random.choice(cls.CITIES)}"

    @classmethod
    def generate_violations(cls, count=200):
        """Generate a batch of realistic violation records."""
        from models.violation_fine import ViolationFine
        
        violations = []
        now = datetime.now()
        
        # Dynamically fetch configured fine amounts
        fine_records = ViolationFine.query.all()
        fine_amounts = {f.violation_type: f.base_amount for f in fine_records}
        if not fine_amounts:
            fine_amounts = {'no_helmet': 1000, 'red_light': 5000}
            
        violation_types = list(fine_amounts.keys())

        for _ in range(count):
            v_type = random.choice(violation_types)

            # Spread across last 30 days with realistic time distribution
            days_ago = random.randint(0, 30)
            # Peak hours: 8-10 AM and 5-8 PM
            hour_weights = [1]*6 + [2]*2 + [5]*2 + [3]*2 + [2]*3 + [1]*2 + [5]*3 + [3]*2 + [1]*3
            hour = random.choices(range(24), weights=hour_weights[:24], k=1)[0]
            minute = random.randint(0, 59)
            dt = now - timedelta(days=days_ago, hours=random.randint(0,5))
            dt = dt.replace(hour=hour, minute=minute, second=random.randint(0,59))

            status = random.choices(
                ['pending', 'paid', 'disputed'],
                weights=[50, 40, 10],
                k=1
            )[0]

            violations.append({
                'vehicle_number': cls.generate_plate(),
                'owner_name': cls.generate_name(),
                'address': cls.generate_address(),
                'violation_type': v_type,
                'fine_amount': fine_amounts[v_type],
                'date_time': dt,
                'location': random.choice(cls.LOCATIONS),
                'status': status,
                'image_path': '',
                'confidence': round(random.uniform(0.65, 0.98), 3)
            })

        return violations
