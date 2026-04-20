"""
Violation Controller — Business logic for violation CRUD operations.
Separates database operations from route handlers.
"""
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from models.violation import db, Violation


class ViolationController:
    """Handles all violation-related business logic."""

    @staticmethod
    def create_violation(data):
        """Create a new violation record."""
        violation = Violation(
            vehicle_number=data.get('vehicle_number', 'UNKNOWN'),
            owner_name=data.get('owner_name', 'Unknown Owner'),
            address=data.get('address', 'Address not available'),
            violation_type=data.get('violation_type', 'no_helmet'),
            fine_amount=data.get('fine_amount', 1000),
            date_time=datetime.fromisoformat(data['date_time']) if 'date_time' in data else datetime.utcnow(),
            location=data.get('location', 'Unknown Location'),
            status=data.get('status', 'pending'),
            image_path=data.get('image_path', ''),
            confidence=data.get('confidence', 0.0)
        )
        db.session.add(violation)
        db.session.commit()
        return violation.to_dict()

    @staticmethod
    def get_all_violations(page=1, per_page=20):
        """Fetch all violations with pagination."""
        pagination = Violation.query.order_by(
            Violation.date_time.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        return {
            'violations': [v.to_dict() for v in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }

    @staticmethod
    def get_violation_by_id(violation_id):
        """Fetch a single violation by ID."""
        violation = Violation.query.get(violation_id)
        if violation:
            return violation.to_dict()
        return None

    @staticmethod
    def filter_violations(filters):
        """Filter violations by date range, type, vehicle number, status."""
        query = Violation.query

        # Filter by violation type
        if filters.get('violation_type'):
            query = query.filter(Violation.violation_type == filters['violation_type'])

        # Filter by vehicle number (partial match)
        if filters.get('vehicle_number'):
            query = query.filter(
                Violation.vehicle_number.ilike(f"%{filters['vehicle_number']}%")
            )

        # Filter by status
        if filters.get('status'):
            query = query.filter(Violation.status == filters['status'])

        # Filter by location
        if filters.get('location'):
            query = query.filter(
                Violation.location.ilike(f"%{filters['location']}%")
            )

        # Filter by date range
        if filters.get('start_date'):
            start = datetime.fromisoformat(filters['start_date'])
            query = query.filter(Violation.date_time >= start)

        if filters.get('end_date'):
            end = datetime.fromisoformat(filters['end_date'])
            query = query.filter(Violation.date_time <= end)

        # Pagination
        page = int(filters.get('page', 1))
        per_page = int(filters.get('per_page', 20))

        pagination = query.order_by(
            Violation.date_time.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        return {
            'violations': [v.to_dict() for v in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }

    @staticmethod
    def get_stats():
        """Generate summary statistics."""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Total counts
        total_violations = Violation.query.count()
        total_fines = db.session.query(func.sum(Violation.fine_amount)).scalar() or 0
        pending_count = Violation.query.filter(Violation.status == 'pending').count()
        today_count = Violation.query.filter(Violation.date_time >= today).count()

        # By violation type
        by_type = db.session.query(
            Violation.violation_type,
            func.count(Violation.id),
            func.sum(Violation.fine_amount)
        ).group_by(Violation.violation_type).all()

        type_stats = {
            row[0]: {'count': row[1], 'total_fine': row[2] or 0}
            for row in by_type
        }

        # By location (top 10)
        by_location = db.session.query(
            Violation.location,
            func.count(Violation.id)
        ).group_by(Violation.location).order_by(
            func.count(Violation.id).desc()
        ).limit(10).all()

        location_stats = [
            {'location': row[0], 'count': row[1]}
            for row in by_location
        ]

        # Violations per day (last 30 days)
        daily_stats = db.session.query(
            func.date(Violation.date_time).label('date'),
            func.count(Violation.id).label('count'),
            func.sum(Violation.fine_amount).label('fines')
        ).filter(
            Violation.date_time >= month_ago
        ).group_by(
            func.date(Violation.date_time)
        ).order_by(
            func.date(Violation.date_time)
        ).all()

        daily = [
            {
                'date': str(row[0]),
                'count': row[1],
                'fines': row[2] or 0
            }
            for row in daily_stats
        ]

        # By hour of day
        hourly_stats = db.session.query(
            func.strftime('%H', Violation.date_time).label('hour'),
            func.count(Violation.id).label('count')
        ).group_by(
            func.strftime('%H', Violation.date_time)
        ).all()

        hourly = [
            {'hour': int(row[0]) if row[0] else 0, 'count': row[1]}
            for row in hourly_stats
        ]

        # By status
        by_status = db.session.query(
            Violation.status,
            func.count(Violation.id)
        ).group_by(Violation.status).all()

        status_stats = {row[0]: row[1] for row in by_status}

        # Week stats
        week_violations = Violation.query.filter(Violation.date_time >= week_ago).count()
        week_fines = db.session.query(
            func.sum(Violation.fine_amount)
        ).filter(Violation.date_time >= week_ago).scalar() or 0

        return {
            'total_violations': total_violations,
            'total_fines': total_fines,
            'pending_count': pending_count,
            'today_count': today_count,
            'week_violations': week_violations,
            'week_fines': week_fines,
            'by_type': type_stats,
            'by_location': location_stats,
            'by_status': status_stats,
            'daily': daily,
            'hourly': hourly
        }
