import csv
import io
import json
import logging
import os
import re
import secrets
import string
from functools import wraps
from pathlib import Path
from datetime import datetime

from flask import (
    Flask, render_template, request, jsonify, redirect,
    url_for, session, send_from_directory, flash, make_response, abort
)
from werkzeug.utils import secure_filename

from config import Config
from database import db_manager

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
upload_path = Path(Config.UPLOAD_FOLDER)
upload_path.mkdir(parents=True, exist_ok=True)

# Initialize database schema and demo records on startup
with app.app_context():
    try:
        db_manager.init_database(seed_demo=True)
    except Exception as e:
        logger.error(f"Failed to auto-initialize database: {e}")

# Subject Categories List
SUBJECTS = [
    "Computer Science",
    "Electrical Engineering",
    "Electronics & Communication",
    "Mechanical Engineering",
    "Civil Engineering",
    "Physics",
    "Chemistry",
    "Chemical Engineering",
    "Biotechnology",
    "Other"
]

# Standard Issues List
ISSUES_LIST = [
    "Experiment is not loading",
    "Simulation is not working",
    "Website is loading slowly",
    "Incorrect experiment output",
    "Audio or video not working",
    "Login or access problem",
    "Navigation difficulties",
    "Broken links",
    "Display or layout issues",
    "Mobile responsiveness problem",
    "Instructions are unclear",
    "Experiment results are inaccurate",
    "Other"
]

DEVICE_OPTIONS = ["Desktop", "Laptop", "Tablet", "Mobile"]
BROWSER_OPTIONS = ["Chrome", "Firefox", "Edge", "Safari", "Other"]
USER_TYPES = ["Student", "Faculty", "Researcher", "Other"]

def allowed_file(filename):
    """Check if uploaded file has a valid extension."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS

def generate_reference_id():
    """Generate a unique academic reference ID in format IITD-VL-2026-XXXXXX."""
    chars = string.ascii_uppercase + string.digits
    for _ in range(10):
        suffix = "".join(secrets.choice(chars) for _ in range(6))
        ref_id = f"IITD-VL-2026-{suffix}"
        # Verify uniqueness in DB
        existing = db_manager.get_feedback_by_reference(ref_id)
        if not existing:
            return ref_id
    # Fallback with timestamp
    return f"IITD-VL-2026-{int(datetime.now().timestamp()) % 1000000:06d}"

def admin_required(f):
    """Decorator to require admin authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Please sign in to access the administrator dashboard.", "warning")
            return redirect(url_for("admin_login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# ========================================================================
# Frontend Routes
# ========================================================================

@app.route("/")
def index():
    """Main landing page with interactive feedback portal."""
    stats = db_manager.get_feedback_stats()
    return render_template(
        "index.html",
        portal_title=Config.PORTAL_TITLE,
        institute_name=Config.INSTITUTE_NAME,
        subjects=SUBJECTS,
        issues_list=ISSUES_LIST,
        device_options=DEVICE_OPTIONS,
        browser_options=BROWSER_OPTIONS,
        user_types=USER_TYPES,
        stats=stats
    )

@app.route("/feedback/<reference_id>")
def feedback_receipt(reference_id):
    """Standalone feedback submission receipt / summary view."""
    record = db_manager.get_feedback_by_reference(reference_id)
    if not record:
        flash("Feedback record not found. Please verify the reference ID.", "danger")
        return redirect(url_for("index"))
    return render_template(
        "success.html",
        record=record,
        portal_title=Config.PORTAL_TITLE
    )

@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    """API endpoint to validate and process feedback submissions."""
    try:
        # Determine if submission is anonymous
        is_anonymous = request.form.get("anonymous_status") in ("1", "true", "True", "on")

        # Collect personal information
        full_name = request.form.get("full_name", "").strip() if not is_anonymous else "Anonymous User"
        email = request.form.get("email", "").strip() if not is_anonymous else None
        mobile_number = request.form.get("mobile_number", "").strip() if not is_anonymous else None
        user_type = request.form.get("user_type", "Student").strip()

        # Collect lab information
        subject = request.form.get("subject", "").strip()
        experiment_name = request.form.get("experiment_name", "").strip()
        experiment_url = request.form.get("experiment_url", "").strip()
        device = request.form.get("device", "Laptop").strip()
        browser = request.form.get("browser", "Chrome").strip()

        # Collect ratings
        try:
            overall_rating = int(request.form.get("overall_rating", 0))
            experiment_rating = int(request.form.get("experiment_rating", 0))
            navigation_rating = int(request.form.get("navigation_rating", 0))
            technical_rating = int(request.form.get("technical_rating", 0))
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Invalid rating format. All ratings must be integers between 1 and 5."
            }), 400

        # Collect issues
        selected_issues = request.form.getlist("selected_issues")
        # Check if 'Other' issue specified
        other_issue_desc = request.form.get("other_issue_desc", "").strip()
        if "Other" in selected_issues and other_issue_desc:
            selected_issues = [iss if iss != "Other" else f"Other: {other_issue_desc}" for iss in selected_issues]

        technical_details = request.form.get("technical_details", "").strip()

        # Experience descriptions
        experience_description = request.form.get("experience_description", "").strip()
        positive_experience = request.form.get("positive_experience", "").strip()
        improvement_suggestions = request.form.get("improvement_suggestions", "").strip()
        recommendation = request.form.get("recommendation", "Yes").strip()

        # ========================================================================
        # Server-side Validation
        # ========================================================================
        errors = []

        if not is_anonymous:
            if not full_name:
                errors.append("Full Name is required when submitting non-anonymously.")
            if not email:
                errors.append("Valid Email Address is required.")
            elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
                errors.append("Please provide a valid email address.")
            if mobile_number and not re.match(r"^\+?[\d\s\-()]{7,18}$", mobile_number):
                errors.append("Please provide a valid mobile number format.")

        if user_type not in USER_TYPES:
            user_type = "Student"

        if not subject:
            errors.append("Please select a Subject / Laboratory.")

        if not experiment_name:
            errors.append("Experiment Name is required.")

        for r_name, r_val in [
            ("Overall Experience", overall_rating),
            ("Quality of Experiment", experiment_rating),
            ("Ease of Navigation", navigation_rating),
            ("Technical Performance", technical_rating)
        ]:
            if r_val < 1 or r_val > 5:
                errors.append(f"Please provide a star rating (1-5) for {r_name}.")

        if not experience_description:
            errors.append("Please describe your experience in the text area.")
        elif len(experience_description) < 10:
            errors.append("Experience description must be at least 10 characters long.")
        elif len(experience_description) > 2000:
            errors.append("Experience description cannot exceed 2000 characters.")

        if recommendation not in ["Yes", "No", "Maybe"]:
            recommendation = "Yes"

        if errors:
            return jsonify({
                "success": False,
                "message": errors[0],
                "errors": errors
            }), 400

        # ========================================================================
        # Screenshot Processing
        # ========================================================================
        saved_screenshot_names = []
        uploaded_files = request.files.getlist("screenshots")

        for file in uploaded_files:
            if file and file.filename:
                orig_filename = secure_filename(file.filename)
                if not allowed_file(orig_filename):
                    return jsonify({
                        "success": False,
                        "message": f"Unsupported file type: '{orig_filename}'. Allowed: PNG, JPG, JPEG, WEBP."
                    }), 400

                # Check individual file size (10 MB limit)
                file.seek(0, os.SEEK_END)
                file_length = file.tell()
                file.seek(0)
                if file_length > Config.MAX_FILE_SIZE_MB * 1024 * 1024:
                    return jsonify({
                        "success": False,
                        "message": f"File '{orig_filename}' exceeds the maximum allowed size of 10 MB."
                    }), 400

                # Generate secure unique filename
                ext = orig_filename.rsplit(".", 1)[1].lower()
                unique_name = f"ss_{secrets.token_hex(8)}_{int(datetime.now().timestamp())}.{ext}"
                save_destination = upload_path / unique_name
                file.save(str(save_destination))
                saved_screenshot_names.append(unique_name)

        # Generate unique reference ID
        reference_id = generate_reference_id()

        record_data = {
            "reference_id": reference_id,
            "full_name": None if is_anonymous else full_name,
            "email": None if is_anonymous else email,
            "mobile_number": None if is_anonymous else mobile_number,
            "user_type": user_type,
            "subject": subject,
            "experiment_name": experiment_name,
            "experiment_url": experiment_url if experiment_url else None,
            "device": device,
            "browser": browser,
            "overall_rating": overall_rating,
            "experiment_rating": experiment_rating,
            "navigation_rating": navigation_rating,
            "technical_rating": technical_rating,
            "selected_issues": selected_issues,
            "technical_details": technical_details,
            "experience_description": experience_description,
            "positive_experience": positive_experience,
            "improvement_suggestions": improvement_suggestions,
            "recommendation": recommendation,
            "anonymous_status": is_anonymous,
            "screenshot_paths": saved_screenshot_names
        }

        result = db_manager.insert_feedback(record_data)

        logger.info(f"Feedback submitted successfully. Ref: {reference_id}, ID: {result['feedback_id']}")

        return jsonify({
            "success": True,
            "message": "Thank You for Your Valuable Feedback!",
            "sub_message": "Your experience matters to us. Your feedback has been successfully submitted and will help improve the IIT Delhi Virtual Labs experience.",
            "reference_id": reference_id,
            "feedback_id": result["feedback_id"],
            "redirect_url": url_for("feedback_receipt", reference_id=reference_id)
        }), 201

    except Exception as e:
        logger.error(f"Error handling feedback submission: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": "An unexpected server error occurred while processing your feedback. Please try again."
        }), 500

@app.route("/uploads/<filename>")
def serve_upload(filename):
    """Safely serve uploaded screenshots."""
    safe_name = secure_filename(filename)
    return send_from_directory(Config.UPLOAD_FOLDER, safe_name)

# ========================================================================
# Administrator Routes
# ========================================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login page and handler."""
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            session["is_admin"] = True
            session["admin_username"] = username
            session["login_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            flash("Welcome to the IIT Delhi Virtual Labs Administrator Dashboard.", "success")
            next_url = request.args.get("next") or url_for("admin_dashboard")
            return redirect(next_url)
        else:
            flash("Invalid administrator credentials. Please try again.", "danger")

    return render_template("admin_login.html", portal_title=Config.PORTAL_TITLE)

@app.route("/admin/logout")
def admin_logout():
    """Admin logout handler."""
    session.pop("is_admin", None)
    session.pop("admin_username", None)
    session.pop("login_time", None)
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("admin_login"))

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    """Admin dashboard to view, search, filter, and inspect feedback."""
    filters = {
        "subject": request.args.get("subject", "").strip(),
        "rating": request.args.get("rating", "").strip(),
        "user_type": request.args.get("user_type", "").strip(),
        "issue": request.args.get("issue", "").strip(),
        "anonymous": request.args.get("anonymous", "").strip(),
        "search": request.args.get("search", "").strip()
    }
    # Clean empty filters
    active_filters = {k: v for k, v in filters.items() if v}

    records = db_manager.get_all_feedback(active_filters)
    stats = db_manager.get_feedback_stats()

    return render_template(
        "admin_dashboard.html",
        records=records,
        stats=stats,
        filters=filters,
        subjects=SUBJECTS,
        issues_list=ISSUES_LIST,
        user_types=USER_TYPES,
        portal_title=Config.PORTAL_TITLE
    )

@app.route("/admin/api/feedback/<int:feedback_id>")
@admin_required
def admin_get_feedback(feedback_id):
    """API endpoint to retrieve single feedback record details for modal view."""
    record = db_manager.get_feedback_by_id(feedback_id)
    if not record:
        return jsonify({"success": False, "message": "Record not found"}), 404
    return jsonify({"success": True, "data": record})

@app.route("/admin/api/feedback/<int:feedback_id>/delete", methods=["POST"])
@admin_required
def admin_delete_feedback(feedback_id):
    """Delete a feedback record and clean up associated files."""
    success, screenshots = db_manager.delete_feedback(feedback_id)
    if success:
        # Clean up files from disk
        for filename in screenshots:
            try:
                target = upload_path / secure_filename(filename)
                if target.exists():
                    target.unlink()
            except Exception as e:
                logger.warning(f"Could not delete image {filename}: {e}")
        return jsonify({"success": True, "message": "Feedback record deleted successfully."})
    return jsonify({"success": False, "message": "Record could not be found or deleted."}), 400

@app.route("/admin/export/csv")
@admin_required
def admin_export_csv():
    """Export filtered feedback records to CSV file."""
    filters = {
        "subject": request.args.get("subject", "").strip(),
        "rating": request.args.get("rating", "").strip(),
        "user_type": request.args.get("user_type", "").strip(),
        "issue": request.args.get("issue", "").strip(),
        "search": request.args.get("search", "").strip()
    }
    active_filters = {k: v for k, v in filters.items() if v}
    records = db_manager.get_all_feedback(active_filters)

    si = io.StringIO()
    writer = csv.writer(si)

    # Header
    writer.writerow([
        "Reference ID",
        "Submitted At",
        "Anonymous",
        "Full Name",
        "Email",
        "Mobile Number",
        "User Type",
        "Subject",
        "Experiment Name",
        "Experiment URL",
        "Device",
        "Browser",
        "Overall Rating",
        "Experiment Rating",
        "Navigation Rating",
        "Technical Rating",
        "Selected Issues",
        "Technical Details",
        "Experience Description",
        "Positive Experience",
        "Improvement Suggestions",
        "Recommendation",
        "Screenshot Count"
    ])

    for r in records:
        writer.writerow([
            r["reference_id"],
            r["created_at"],
            "Yes" if r["anonymous_status"] else "No",
            r.get("full_name") or "Anonymous",
            r.get("email") or "N/A",
            r.get("mobile_number") or "N/A",
            r.get("user_type", "Student"),
            r["subject"],
            r["experiment_name"],
            r.get("experiment_url") or "",
            r.get("device", ""),
            r.get("browser", ""),
            r["overall_rating"],
            r["experiment_rating"],
            r["navigation_rating"],
            r["technical_rating"],
            "; ".join(r.get("selected_issues", [])),
            r.get("technical_details", "") or "",
            r.get("experience_description", "") or "",
            r.get("positive_experience", "") or "",
            r.get("improvement_suggestions", "") or "",
            r.get("recommendation", "Yes"),
            len(r.get("screenshot_paths", []))
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = (
        f"attachment; filename=iitd_virtual_labs_feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    output.headers["Content-type"] = "text/csv; charset=utf-8"
    return output

# ========================================================================
# Error Handlers
# ========================================================================

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle uploads exceeding total payload limit."""
    return jsonify({
        "success": False,
        "message": "Total upload size exceeded maximum limit (25 MB). Please compress or reduce images."
    }), 413

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

