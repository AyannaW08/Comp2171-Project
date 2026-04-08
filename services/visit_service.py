"""
visit_service.py
Handles all business logic related to school visits.
Routes in app.py should call these functions instead of querying the DB directly.
"""

from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import and_
from models import db, Visit, School


class VisitService:
    """Service class responsible for all visit-related operations."""

    @staticmethod
    def get_all_visits() -> List[Visit]:
        """Return all visits ordered by date descending (most recent first)."""
        return Visit.query.order_by(Visit.visit_date.desc()).all()

    @staticmethod
    def get_visit_or_404(visit_id: int) -> Visit:
        """Return a visit by ID or abort with 404 if not found."""
        return Visit.query.get_or_404(visit_id)

    @staticmethod
    def get_filtered_visits(
        status: Optional[str] = None,
        school_id: Optional[int] = None,
        visit_date: Optional[date] = None,
    ) -> List[Visit]:
        """
        Return visits filtered by any combination of status, school, or date.
        Used by the View Schedule feature (Feature 5).
        """
        query = Visit.query

        if status:
            query = query.filter(Visit.status == status)
        if school_id:
            query = query.filter(Visit.school_id == school_id)
        if visit_date:
            query = query.filter(Visit.visit_date == visit_date)

        return query.order_by(Visit.visit_date.desc()).all()

    @staticmethod
    def has_conflict(visit_date: date, visit_time: str) -> bool:
        """
        Check if a visit is already scheduled at the given date and time.
        Used for conflict detection (SRS 3.3).
        """
        return Visit.query.filter(
            and_(Visit.visit_date == visit_date, Visit.visit_time == visit_time)
        ).first() is not None

    @staticmethod
    def schedule_visit(school_id: int, visit_date: date, visit_time: str) -> Visit:
        """
        Create and persist a new Visit.
        Caller is responsible for checking conflicts before calling this.
        """
        visit = Visit(
            school_id=school_id,
            visit_date=visit_date,
            visit_time=visit_time,
            status="Scheduled",
        )
        db.session.add(visit)
        db.session.commit()
        return visit

    @staticmethod
    def delete_visit(visit: Visit) -> None:
        """Delete a visit from the database."""
        db.session.delete(visit)
        db.session.commit()

    @staticmethod
    def mark_completed(visit: Visit) -> Visit:
        """Mark a visit as completed."""
        visit.status = "Completed"
        db.session.commit()
        return visit