"""
FractureAI Scan Routes
========================
Handles X-ray upload, AI analysis, heatmap generation,
PDF report creation, and result display.
"""

import os
import uuid
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user

from database.db import db, Scan
from models.fracture_model import FractureDetector, preprocess_image
from models.grad_cam import generate_gradcam
from utils.pdf_report import generate_pdf_report
from utils.recovery import get_recovery_suggestions
from utils.doctor_suggest import get_doctor_recommendation
from utils.email_service import send_report_email

# Create scan blueprint
scan_bp = Blueprint("scan", __name__)

# Global detector instance (loaded once)
_detector = None


def get_detector():
    """Get or create the fracture detector singleton."""
    global _detector
    if _detector is None:
        model_path = current_app.config.get("MODEL_PATH", "")
        _detector = FractureDetector(model_path=model_path)
    return _detector


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg"})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


@scan_bp.route("/scan", methods=["GET"])
@login_required
def scan_page():
    """Render the X-ray upload/scan page."""
    return render_template("scan.html")


@scan_bp.route("/scan/upload", methods=["POST"])
@login_required
def upload_scan():
    """
    Handle X-ray image upload and run AI analysis.

    Steps:
    1. Save uploaded image
    2. Run fracture detection CNN
    3. Generate Grad-CAM heatmap
    4. Get recovery suggestions
    5. Get doctor recommendations
    6. Generate PDF report
    7. Save scan to database
    8. Redirect to results page
    """
    # Check if file was uploaded
    if "xray_image" not in request.files:
        flash("No image file uploaded.", "error")
        return redirect(url_for("scan.scan_page"))

    file = request.files["xray_image"]
    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("scan.scan_page"))

    if not allowed_file(file.filename):
        flash("Invalid file type. Please upload a PNG, JPG, or JPEG image.", "error")
        return redirect(url_for("scan.scan_page"))

    # Get body part from form
    body_part = request.form.get("body_part", "Unknown")

    # Generate unique filename
    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    # Save uploaded file
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    original_path = os.path.join(upload_dir, unique_name)
    file.save(original_path)

    # ── Step 1: Run AI Fracture Detection ──
    detector = get_detector()
    result = detector.predict(original_path)

    # ── Step 2: Generate Grad-CAM Heatmap ──
    heatmap_name = f"heatmap_{unique_name}"
    heatmap_path = os.path.join(upload_dir, heatmap_name)
    try:
        model = detector.get_model()
        generate_gradcam(model, original_path, heatmap_path)
    except Exception as e:
        print(f"[FractureAI] Heatmap generation error: {e}")
        heatmap_path = ""

    # ── Step 3: Get Recovery Suggestions ──
    recovery = ""
    if result["fracture_detected"]:
        recovery = get_recovery_suggestions(
            result["severity"],
            result["fracture_type"],
            body_part
        )

    # ── Step 4: Get Doctor Recommendations ──
    doctor_rec = ""
    if result["fracture_detected"]:
        doctor_rec = get_doctor_recommendation(
            result["severity"],
            result["fracture_type"],
            body_part
        )

    # ── Step 5: Save Scan to Database ──
    scan = Scan(
        user_id=current_user.id,
        original_image=unique_name,
        heatmap_image=heatmap_name if heatmap_path else "",
        fracture_detected=result["fracture_detected"],
        confidence=result["confidence"],
        severity=result["severity"],
        fracture_type=result["fracture_type"],
        recovery_suggestion=recovery,
        doctor_recommendation=doctor_rec,
        body_part=body_part,
    )
    db.session.add(scan)
    db.session.commit()

    # ── Step 6: Generate PDF Report ──
    report_name = f"report_{scan.id}_{unique_name.rsplit('.', 1)[0]}.pdf"
    report_dir = current_app.config["REPORT_FOLDER"]
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, report_name)

    try:
        scan_data = {
            "fracture_detected": result["fracture_detected"],
            "confidence": result["confidence"] * 100,
            "severity": result["severity"],
            "fracture_type": result["fracture_type"],
            "recovery_suggestion": recovery,
            "doctor_recommendation": doctor_rec,
            "body_part": body_part,
            "original_image": original_path,
            "heatmap_image": heatmap_path if heatmap_path else "",
            "scanned_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        user_data = {
            "full_name": current_user.full_name,
            "email": current_user.email,
            "username": current_user.username,
        }
        generate_pdf_report(scan_data, user_data, report_path)
        scan.report_path = report_name
        db.session.commit()
    except Exception as e:
        print(f"[FractureAI] PDF generation error: {e}")

    flash("X-ray analysis complete!", "success")
    return redirect(url_for("scan.result_page", scan_id=scan.id))


@scan_bp.route("/result/<int:scan_id>")
@login_required
def result_page(scan_id):
    """Display the scan result page with all analysis details."""
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first()
    if not scan:
        flash("Scan not found.", "error")
        return redirect(url_for("scan.scan_page"))

    return render_template("result.html", scan=scan)


@scan_bp.route("/download-report/<int:scan_id>")
@login_required
def download_report(scan_id):
    """Download the PDF report for a scan."""
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first()
    if not scan or not scan.report_path:
        flash("Report not found.", "error")
        return redirect(url_for("scan.scan_page"))

    report_path = os.path.join(current_app.config["REPORT_FOLDER"], scan.report_path)
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True, download_name="FractureAI_Report.pdf")
    else:
        flash("Report file not found on server.", "error")
        return redirect(url_for("scan.result_page", scan_id=scan_id))


@scan_bp.route("/email-report/<int:scan_id>", methods=["POST"])
@login_required
def email_report(scan_id):
    """Email the PDF report to the patient."""
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first()
    if not scan or not scan.report_path:
        flash("Report not found.", "error")
        return redirect(url_for("scan.result_page", scan_id=scan_id))

    report_path = os.path.join(current_app.config["REPORT_FOLDER"], scan.report_path)
    summary = f"Fracture: {'Yes' if scan.fracture_detected else 'No'} | Severity: {scan.severity} | Confidence: {scan.confidence * 100:.1f}%"

    success = send_report_email(
        current_user.email,
        current_user.full_name,
        report_path,
        summary
    )

    if success:
        flash(f"Report sent to {current_user.email}!", "success")
    else:
        flash("Failed to send email. Please check email configuration.", "error")

    return redirect(url_for("scan.result_page", scan_id=scan_id))
