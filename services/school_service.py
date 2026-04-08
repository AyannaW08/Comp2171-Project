"""
school_service.py
Handles all business logic related to schools.
Routes in app.py should call these functions instead of querying the DB directly.
"""

from typing import Optional, List
from models import db, School


class SchoolService:
    """Service class responsible for all school-related operations."""

    @staticmethod
    def get_all_schools() -> List[School]:
        """Return all schools ordered alphabetically by name."""
        return School.query.order_by(School.name).all()

    @staticmethod
    def search_schools(term: str) -> List[School]:
        """Return schools whose name matches the search term (case-insensitive)."""
        return School.query.filter(School.name.ilike(f"%{term}%")).order_by(School.name).all()

    @staticmethod
    def get_school_by_id(school_id: int) -> Optional[School]:
        """Return a single school by ID, or None if not found."""
        return School.query.get(school_id)

    @staticmethod
    def get_school_or_404(school_id: int) -> School:
        """Return a school by ID or abort with 404 if not found."""
        return School.query.get_or_404(school_id)

    @staticmethod
    def name_exists(name: str, exclude_id: Optional[int] = None) -> bool:
        """
        Check if a school with the given name already exists.
        Pass exclude_id when editing so the school being edited is not flagged as a duplicate.
        """
        query = School.query.filter(db.func.lower(School.name) == name.lower())
        if exclude_id is not None:
            query = query.filter(School.id != exclude_id)
        return query.first() is not None

    @staticmethod
    def add_school(data: dict) -> School:
        """
        Create and persist a new School from a dictionary of field values.
        Expects keys: name, address, contact_person, contact_phone,
                      contact_email, capacity, start_time, end_time,
                      exam_dates, holidays, num_teachers
        """
        school = School(
            name=data["name"],
            address=data["address"],
            contact_person=data["contact_person"],
            contact_phone=data.get("contact_phone"),
            contact_email=data.get("contact_email"),
            capacity=data.get("capacity"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            exam_dates=data.get("exam_dates"),
            holidays=data.get("holidays"),
            num_teachers=data.get("num_teachers"),
        )
        db.session.add(school)
        db.session.commit()
        return school

    @staticmethod
    def update_school(school: School, data: dict) -> School:
        """
        Update an existing School object with new field values from a dictionary.
        Commits the changes to the database.
        """
        school.name = data["name"]
        school.address = data["address"]
        school.contact_person = data["contact_person"]
        school.contact_phone = data.get("contact_phone")
        school.contact_email = data.get("contact_email")
        school.capacity = data.get("capacity")
        school.start_time = data.get("start_time")
        school.end_time = data.get("end_time")
        school.exam_dates = data.get("exam_dates")
        school.holidays = data.get("holidays")
        school.num_teachers = data.get("num_teachers")
        db.session.commit()
        return school

    @staticmethod
    def delete_school(school: School) -> None:
        """Delete a school from the database."""
        db.session.delete(school)
        db.session.commit()