"""
models.py
SQLAlchemy model definitions for the Captain I Can! CDMS.
Imported by app.py, services, and seed_schools.py.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class School(db.Model):
    """Represents a school in the CDMS."""
    __tablename__ = "schools"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(120))
    capacity = db.Column(db.Integer)
    start_time = db.Column(db.String(20))
    end_time = db.Column(db.String(20))
    exam_dates = db.Column(db.String(255))
    holidays = db.Column(db.String(255))
    num_teachers = db.Column(db.Integer)

    visits = db.relationship('Visit', backref='school', lazy=True)

    def to_dict(self) -> Dict[str, Any]:
        """Return school data as a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "contact_person": self.contact_person,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "capacity": self.capacity,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "exam_dates": self.exam_dates,
            "holidays": self.holidays,
            "num_teachers": self.num_teachers,
        }

    def __repr__(self):
        return f"<School id={self.id} name={self.name!r}>"


class Visit(db.Model):
    """Represents a scheduled visit to a school."""
    __tablename__ = "visits"

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    visit_time = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Scheduled')

    feedbacks = db.relationship('Feedback', backref='visit', lazy=True)

    def __repr__(self):
        return f"<Visit id={self.id} school_id={self.school_id} date={self.visit_date}>"


class Feedback(db.Model):
    """Stores feedback submitted after a school visit."""
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=True)
    Name = db.Column(db.String(100), nullable=False)
    School_name = db.Column(db.String(150), nullable=False)
    Email = db.Column(db.String(120), nullable=False)
    Feedback = db.Column(db.Text, nullable=False)
    TripDate = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Feedback id={self.id} name={self.Name!r}>"