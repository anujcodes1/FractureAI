"""
FractureAI Dashboard Routes
==============================
Patient history dashboard with scan records,
statistics, and visual analytics.
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from database.db import Scan
from sqlalchemy import func

# Create dashboard blueprint
dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    """
    Render the patient history dashboard.
    Shows all past scans with summary statistics.
    """
    # Fetch all scans for the current user, newest first
    scans = Scan.query.filter_by(user_id=current_user.id)\
                      .order_by(Scan.scanned_at.desc())\
                      .all()

    # Calculate statistics
    total_scans = len(scans)
    fractures_detected = sum(1 for s in scans if s.fracture_detected)
    normal_scans = total_scans - fractures_detected

    # Severity breakdown
    severity_counts = {"Low": 0, "Medium": 0, "High": 0}
    for s in scans:
        if s.severity in severity_counts:
            severity_counts[s.severity] += 1

    # Average confidence
    avg_confidence = 0
    if total_scans > 0:
        avg_confidence = sum(s.confidence for s in scans) / total_scans * 100

    stats = {
        "total_scans": total_scans,
        "fractures_detected": fractures_detected,
        "normal_scans": normal_scans,
        "severity_counts": severity_counts,
        "avg_confidence": round(avg_confidence, 1),
    }

    return render_template("dashboard.html", scans=scans, stats=stats)


@dashboard_bp.route("/api/dashboard-stats")
@login_required
def dashboard_stats_api():
    """
    API endpoint returning dashboard statistics as JSON.
    Used by frontend charts and dynamic updates.
    """
    scans = Scan.query.filter_by(user_id=current_user.id).all()

    total = len(scans)
    fractures = sum(1 for s in scans if s.fracture_detected)

    severity = {"Low": 0, "Medium": 0, "High": 0}
    body_parts = {}
    monthly = {}

    for s in scans:
        if s.severity in severity:
            severity[s.severity] += 1

        bp = s.body_part or "Unknown"
        body_parts[bp] = body_parts.get(bp, 0) + 1

        month_key = s.scanned_at.strftime("%Y-%m") if s.scanned_at else "Unknown"
        monthly[month_key] = monthly.get(month_key, 0) + 1

    return jsonify({
        "total_scans": total,
        "fractures_detected": fractures,
        "normal_scans": total - fractures,
        "severity_breakdown": severity,
        "body_parts": body_parts,
        "monthly_scans": monthly,
    })
