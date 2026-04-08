"""
validators/school_validator.py
Validates school form data before it is passed to the service layer.
Keeps validation logic separate from routes and services.
"""

from typing import Dict, Optional


class SchoolValidator:
    """
    Validates all fields submitted through the Add School and Edit School forms.
    After calling validate(), check self.errors for any problems,
    and use the parsed field attributes to pass clean data to SchoolService.
    """

    def __init__(self, form_data):
        self._form = form_data
        self.errors: Dict[str, str] = {}

        # Cleaned field values — populated after validate() is called
        self.name: str = ""
        self.address: str = ""
        self.contact_person: str = ""
        self.contact_phone: str = ""
        self.contact_email: str = ""
        self.capacity: Optional[int] = None
        self.start_time: str = ""
        self.end_time: str = ""
        self.exam_dates: str = ""
        self.holidays: str = ""
        self.num_teachers: Optional[int] = None

    def validate(self) -> bool:
        """
        Run all validation checks.
        Returns True if all data is valid, False if any errors were found.
        """
        self._validate_text_fields()
        self._validate_capacity()
        self._validate_num_teachers()
        self._validate_email()
        return len(self.errors) == 0

    def to_dict(self) -> dict:
        """
        Return validated field values as a dictionary.
        Pass this directly to SchoolService.add_school() or SchoolService.update_school().
        Only call this after validate() returns True.
        """
        return {
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

    # ------------------------------------------------------------------
    # Private validation methods
    # ------------------------------------------------------------------

    def _validate_text_fields(self):
        """Strip and check that required text fields are not empty."""
        self.name = self._form.get("name", "").strip()
        self.address = self._form.get("address", "").strip()
        self.contact_person = self._form.get("contact_person", "").strip()
        self.contact_phone = self._form.get("contact_phone", "").strip()
        self.contact_email = self._form.get("contact_email", "").strip()
        self.start_time = self._form.get("start_time", "").strip()
        self.end_time = self._form.get("end_time", "").strip()
        self.exam_dates = self._form.get("exam_dates", "").strip()
        self.holidays = self._form.get("holidays", "").strip()

        if not self.name:
            self.errors["name"] = "School name is required."
        if not self.address:
            self.errors["address"] = "Address is required."
        if not self.contact_person:
            self.errors["contact_person"] = "Contact person is required."

    def _validate_capacity(self):
        """Validate that capacity is a non-negative integer if provided."""
        raw = self._form.get("capacity", "").strip()
        if raw == "":
            self.capacity = None
            return
        try:
            self.capacity = int(raw)
            if self.capacity < 0:
                self.errors["capacity"] = "Capacity cannot be negative."
        except ValueError:
            self.errors["capacity"] = "Capacity must be a whole number."

    def _validate_num_teachers(self):
        """Validate that num_teachers is a non-negative integer if provided."""
        raw = self._form.get("num_teachers", "").strip()
        if raw == "":
            self.num_teachers = None
            return
        try:
            self.num_teachers = int(raw)
            if self.num_teachers < 0:
                self.errors["num_teachers"] = "Number of teachers cannot be negative."
        except ValueError:
            self.errors["num_teachers"] = "Number of teachers must be a whole number."

    def _validate_email(self):
        """Basic check that the email contains an @ symbol."""
        if self.contact_email and "@" not in self.contact_email:
            self.errors["contact_email"] = "Please enter a valid email address."