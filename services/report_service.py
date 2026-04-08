"""
services/report_service.py
Handles all business logic for generating summary reports.
Routes in app.py should call these methods instead of building queries directly.
"""

import csv
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from models import Visit


class ReportService:
    """
    Service class responsible for generating and exporting visit summary reports.
    Supports filtering by date range, school, or partner (Feature 4).
    """

    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(exist_ok=True)

    def build_summary(
        self,
        report_type: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        school_id: Optional[int] = None,
        partner_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Query the visits table and return summary statistics.
        Filters are applied based on report_type and the provided parameters.
        """
        query = Visit.query

        # Date range filter
        if start_date and end_date:
            query = query.filter(Visit.visit_date.between(start_date, end_date))
        elif start_date:
            query = query.filter(Visit.visit_date >= start_date)
        elif end_date:
            query = query.filter(Visit.visit_date <= end_date)

        # School filter (only applied for by_school report type)
        if report_type == "by_school" and school_id is not None:
            query = query.filter(Visit.school_id == school_id)

        visits = query.all()

        return {
            "number_of_schools": len({v.school_id for v in visits}),
            "number_of_visits": len(visits),
            "total_students": 0,   # placeholder — column not yet tracked
            "total_teachers": 0,
            "total_parents": 0,
        }

    def write_csv(self, summary: Dict[str, Any], report_type: str) -> Path:
        """
        Write a summary dictionary to a timestamped CSV file.
        Returns the path to the generated file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_{report_type}_{timestamp}.csv"
        output_path = self.reports_dir / filename

        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            for key, value in summary.items():
                writer.writerow([key, value])

        return output_path

    # ------------------------------------------------------------------
    # Static helpers — used by routes to parse raw form field strings
    # ------------------------------------------------------------------

    @staticmethod
    def parse_date(value: str) -> Optional[date]:
        """Parse a date string (YYYY-MM-DD) from a form field. Returns None if empty/invalid."""
        value = value.strip()
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def parse_int(value: str) -> Optional[int]:
        """Parse an integer string from a form field. Returns None if empty/invalid."""
        value = value.strip()
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            return None