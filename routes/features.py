"""
FractureAI Features Routes
==============================
Routes for Health Score, Clinical Suggestions,
Doctor Appointments, and Clinic Locations.
"""

import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from database.db import db, Scan, Appointment
from utils.health_score import calculate_health_score, get_clinical_suggestions
from utils.clinics import get_all_clinics, get_clinic_by_id, search_clinics

# Create features blueprint
features_bp = Blueprint("features", __name__)


@features_bp.route("/health-score")
@login_required
def health_score_page():
    """
    Display the comprehensive bone health score dashboard.
    """
    scans = Scan.query.filter_by(user_id=current_user.id)\
                      .order_by(Scan.scanned_at.desc())\
                      .all()

    health_data = calculate_health_score(scans)

    return render_template("health_score.html",
                           health=health_data,
                           total_scans=len(scans),
                           scans=scans)


@features_bp.route("/clinical-suggestions/<int:scan_id>")
@login_required
def clinical_suggestions_page(scan_id):
    """
    Display detailed clinical suggestions for a specific scan.
    """
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first()
    if not scan:
        flash("Scan not found.", "error")
        return redirect(url_for("dashboard.dashboard"))

    suggestions = get_clinical_suggestions(scan)

    return render_template("clinical_suggestions.html",
                           scan=scan,
                           suggestions=suggestions)


@features_bp.route("/clinics")
@login_required
def clinics_page():
    """
    Display the clinic/hospital directory with interactive listing.
    """
    query = request.args.get("q", "")
    clinic_type = request.args.get("type", "all")

    clinics = get_all_clinics()

    if query:
        clinics = search_clinics(query)
    elif clinic_type != "all":
        clinics = [c for c in clinics if c["type"] == clinic_type]

    return render_template("clinics.html",
                           clinics=clinics,
                           query=query,
                           clinic_type=clinic_type)


@features_bp.route("/appointments")
@login_required
def appointments_page():
    """
    Display user's appointments and booking form.
    """
    appointments = Appointment.query.filter_by(user_id=current_user.id)\
                                    .order_by(Appointment.appointment_date.desc())\
                                    .all()
    clinics = get_all_clinics()

    return render_template("appointments.html",
                           appointments=appointments,
                           clinics=clinics)


@features_bp.route("/appointments/book", methods=["POST"])
@login_required
def book_appointment():
    """
    Book a new doctor appointment.
    """
    clinic_id = request.form.get("clinic_id", type=int)
    doctor_name = request.form.get("doctor_name", "")
    appointment_date_str = request.form.get("appointment_date", "")
    appointment_time = request.form.get("appointment_time", "")
    reason = request.form.get("reason", "")
    notes = request.form.get("notes", "")

    if not clinic_id or not appointment_date_str or not appointment_time:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("features.appointments_page"))

    clinic = get_clinic_by_id(clinic_id)
    if not clinic:
        flash("Selected clinic not found.", "error")
        return redirect(url_for("features.appointments_page"))

    try:
        appointment_date = datetime.strptime(
            f"{appointment_date_str} {appointment_time}", "%Y-%m-%d %H:%M"
        )
    except ValueError:
        flash("Invalid date or time format.", "error")
        return redirect(url_for("features.appointments_page"))

    if appointment_date < datetime.now():
        flash("Cannot book appointments in the past.", "error")
        return redirect(url_for("features.appointments_page"))

    appointment = Appointment(
        user_id=current_user.id,
        clinic_name=clinic["name"],
        clinic_address=clinic["address"],
        doctor_name=doctor_name or "To be assigned",
        appointment_date=appointment_date,
        reason=reason or "Orthopedic Consultation",
        notes=notes,
        status="confirmed",
    )
    db.session.add(appointment)
    db.session.commit()

    flash(f"Appointment booked at {clinic['name']} on {appointment_date.strftime('%B %d, %Y at %I:%M %p')}!", "success")
    return redirect(url_for("features.appointments_page"))


@features_bp.route("/appointments/cancel/<int:appt_id>", methods=["POST"])
@login_required
def cancel_appointment(appt_id):
    """Cancel an existing appointment."""
    appt = Appointment.query.filter_by(id=appt_id, user_id=current_user.id).first()
    if not appt:
        flash("Appointment not found.", "error")
        return redirect(url_for("features.appointments_page"))

    appt.status = "cancelled"
    db.session.commit()

    flash("Appointment cancelled successfully.", "info")
    return redirect(url_for("features.appointments_page"))


@features_bp.route("/api/clinics")
@login_required
def api_clinics():
    """API endpoint for clinic data (JSON)."""
    clinics = get_all_clinics()
    return jsonify(clinics)


@features_bp.route("/api/clinic/<int:clinic_id>")
@login_required
def api_clinic_detail(clinic_id):
    """API endpoint for a single clinic."""
    clinic = get_clinic_by_id(clinic_id)
    if not clinic:
        return jsonify({"error": "Not found"}), 404
    return jsonify(clinic)
