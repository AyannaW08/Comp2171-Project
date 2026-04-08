"""
app.py
Flask application entry point for the Captain I Can! CDMS.
This file contains ONLY route definitions.
All business logic lives in /services and /validators.
"""


from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from functools import wraps
from pathlib import Path
import os

from models import db, School, Visit, Feedback
from FeedbackForm import FeedbackForm
from services.school_service import SchoolService
from services.visit_service import VisitService
from services.report_service import ReportService
from validators.school_validator import SchoolValidator
from datetime import datetime

app = Flask(__name__)
app.secret_key = "very-simple-secret-key"

DATABASE = os.path.join(os.path.dirname(__file__), "cdms.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

REPORTS_DIR = Path("reports")
report_service = ReportService(REPORTS_DIR)


# ========================================
# AUTH DECORATOR
# ========================================

def login_required(f):
    """Protect routes — redirects to login if user is not authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ========================================
# LOGIN / LOGOUT  (Auth)
# ========================================

@app.route("/")
def home():
    if 'logged_in' in session:
        return redirect(url_for("list_schools"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if 'logged_in' in session:
        return redirect(url_for("list_schools"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == "admin" and password == "admin123":
            session['logged_in'] = True
            session['username'] = username
            flash("Welcome! You are now logged in.", "success")
            return redirect(url_for("list_schools"))

        return render_template("login.html", error="Wrong username or password. Please try again.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# ========================================
# SCHOOL ROUTES  (Feature 1 & 2)
# ========================================

@app.route("/schools")
@login_required
def list_schools():
    """Display all schools with optional search (SRS 2.1)."""
    search_term = request.args.get("search", "").strip()
    schools = SchoolService.search_schools(search_term) if search_term else SchoolService.get_all_schools()
    return render_template("schools_list.html", schools=schools, search=search_term)


@app.route("/schools/add", methods=["GET", "POST"])
@login_required
def add_school():
    """Add a new school to the database (Feature 1)."""
    if request.method == "POST":
        validator = SchoolValidator(request.form)

        if not validator.validate():
            flash("Please fix the errors below and try again.", "error")
            return render_template("add_school.html", form_data=request.form, errors=validator.errors)

        if SchoolService.name_exists(validator.name):
            flash("A school with this name already exists.", "error")
            return render_template("add_school.html", form_data=request.form,
                                   errors={"name": "School name already exists."})

        SchoolService.add_school(validator.to_dict())
        flash("School added successfully!", "success")
        return redirect(url_for("list_schools"))

    return render_template("add_school.html", form_data={}, errors={})


@app.route("/schools/<int:school_id>/edit", methods=["GET", "POST"])
@login_required
def edit_school(school_id):
    """Edit an existing school's information (Feature 2)."""
    school = SchoolService.get_school_or_404(school_id)

    if request.method == "POST":
        validator = SchoolValidator(request.form)

        if not validator.validate():
            flash("Please fix the errors below and try again.", "error")
            return render_template("edit_school.html", school=school,
                                   form_data=request.form, errors=validator.errors)

        SchoolService.update_school(school, validator.to_dict())
        flash("School information updated successfully.", "success")
        return redirect(url_for("edit_school", school_id=school_id))

    return render_template("edit_school.html", school=school, form_data=school, errors={})


@app.route("/schools/<int:school_id>/delete", methods=["POST"])
@login_required
def delete_school(school_id):
    """Delete a school from the database."""
    school = SchoolService.get_school_or_404(school_id)
    SchoolService.delete_school(school)
    flash("School deleted successfully.", "success")
    return redirect(url_for("list_schools"))


# ========================================
# VISIT ROUTES  (Feature 3 & 5)
# ========================================

@app.route('/visits')
@login_required
def list_visits():
    """Display all visits with optional filtering by status, school, or date (Feature 5)."""
    status_filter = request.args.get("status", "").strip()
    school_filter = request.args.get("school_id", "").strip()
    date_filter = request.args.get("date", "").strip()

    parsed_date = ReportService.parse_date(date_filter) if date_filter else None
    parsed_school_id = ReportService.parse_int(school_filter) if school_filter else None

    visits = VisitService.get_filtered_visits(
        status=status_filter or None,
        school_id=parsed_school_id,
        visit_date=parsed_date,
    )
    schools = SchoolService.get_all_schools()

    return render_template('visits/list.html', visits=visits, schools=schools,
                           status_filter=status_filter, school_filter=school_filter)


@app.route('/visits/schedule', methods=['GET', 'POST'])
@login_required
def schedule_visit():
    """Schedule a new school visit (Feature 3)."""
    schools = SchoolService.get_all_schools()

    if request.method == 'POST':
        school_id = request.form.get('school_id')
        date_str = request.form.get('visit_date')
        time_str = request.form.get('visit_time')

        if not school_id or not date_str or not time_str:
            flash('All fields are required.', 'error')
            return redirect(url_for('schedule_visit'))

        visit_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        if VisitService.has_conflict(visit_date, time_str):
            flash('Conflict: a visit is already scheduled at this date and time.', 'error')
            return redirect(url_for('schedule_visit'))

        VisitService.schedule_visit(int(school_id), visit_date, time_str)
        flash('Visit scheduled successfully!', 'success')
        return redirect(url_for('list_visits'))

    return render_template('visits/schedule.html', schools=schools)


@app.route('/visits/<int:visit_id>/delete', methods=['POST'])
@login_required
def delete_visit(visit_id):
    """Delete a scheduled visit."""
    visit = VisitService.get_visit_or_404(visit_id)
    VisitService.delete_visit(visit)
    flash('Visit deleted successfully.', 'success')
    return redirect(url_for('list_visits'))


# ========================================
# REPORT ROUTES  (Feature 4)
# ========================================

@app.route("/reports", methods=["GET", "POST"])
@login_required
def generate_report():
    """Generate a summary report by date range, school, or partner (Feature 4)."""
    if request.method == "GET":
        return render_template("report_form.html")

    report_type = request.form.get("report_type", "by_date_range")
    start_date = ReportService.parse_date(request.form.get("start_date", ""))
    end_date = ReportService.parse_date(request.form.get("end_date", ""))
    school_id = ReportService.parse_int(request.form.get("school_id", ""))
    partner_id = ReportService.parse_int(request.form.get("partner_id", ""))

    summary = report_service.build_summary(report_type, start_date, end_date, school_id, partner_id)
    output_path = report_service.write_csv(summary, report_type)

    flash("Report generated successfully.", "success")
    return render_template("report_result.html", summary=summary,
                           report_file_name=output_path.name, report_type=report_type)


@app.route("/reports/download/<filename>")
@login_required
def download_report(filename: str):
    """Download a previously generated CSV report."""
    file_path = REPORTS_DIR / filename
    if not file_path.exists():
        flash("Report file not found.", "error")
        return redirect(url_for("generate_report"))
    return send_file(file_path, as_attachment=True, download_name=filename, mimetype="text/csv")


# ========================================
# FEEDBACK ROUTES  (Feature 6)
# ========================================

@app.route("/feedback", methods=['GET', 'POST'])
def feedback():
    """Allow students and teachers to submit feedback (Feature 6)."""
    form = FeedbackForm()
    school_names = [s.name for s in SchoolService.get_all_schools()]

    if form.validate_on_submit():
        new_feedback = Feedback(
            visit_id=None,
            Name=form.Name.data,
            Email=form.Email.data,
            School_name=form.School_name.data,
            TripDate=form.TripDate.data,
            Feedback=form.Feedback.data,
        )
        db.session.add(new_feedback)
        db.session.commit()
        flash(f'Feedback submitted successfully for {form.Name.data}!', 'success')
        return redirect(url_for('feedback'))

    return render_template('feedback.html', title='Feedback Form', form=form, school_names=school_names)


@app.route("/feedback_db", methods=["GET"])
@login_required
def feedback_db():
    """Admin view: search and browse all submitted feedback."""
    search_query = request.args.get("search", "").strip()
    query = Feedback.query

    if search_query:
        query = query.filter(
            db.or_(
                Feedback.Name.ilike(f"%{search_query}%"),
                Feedback.School_name.ilike(f"%{search_query}%"),
            )
        )

    feedback_list = query.order_by(Feedback.created_at.desc()).all()
    return render_template("feedback_db.html", feedback_list=feedback_list, search=search_query)


@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
@login_required
def delete_feedback(feedback_id):
    """Delete a feedback entry."""
    entry = Feedback.query.get_or_404(feedback_id)
    db.session.delete(entry)
    db.session.commit()
    flash("Feedback entry deleted successfully.", "success")
    return redirect(url_for("feedback_db"))


# ========================================
# RUN
# ========================================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)