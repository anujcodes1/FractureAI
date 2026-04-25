"""
FractureAI API Routes
======================
REST API endpoints for camera scanning, voice commands,
and AJAX-based interactions.
"""

import os
import uuid
import base64
from io import BytesIO

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
try:
    from PIL import Image
    _PIL_AVAILABLE = True
except (ImportError, OSError):
    Image = None
    _PIL_AVAILABLE = False

from database.db import db, Scan
from models.fracture_model import FractureDetector
from models.grad_cam import generate_gradcam
from utils.recovery import get_recovery_suggestions
from utils.doctor_suggest import get_doctor_recommendation, get_specialists_list

# Create API blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api")

# Detector singleton
_detector = None


def get_detector():
    global _detector
    if _detector is None:
        model_path = current_app.config.get("MODEL_PATH", "")
        _detector = FractureDetector(model_path=model_path)
    return _detector


@api_bp.route("/analyze-camera", methods=["POST"])
@login_required
def analyze_camera_frame():
    """
    Analyze a camera frame captured from the live camera feed.
    Receives a base64-encoded image from the frontend.

    Request JSON:
        {
            "image": "data:image/jpeg;base64,...",
            "body_part": "arm"
        }

    Returns:
        JSON with fracture detection results
    """
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "No image data received"}), 400

    if not _PIL_AVAILABLE:
        return jsonify({"error": "Image processing unavailable (Pillow not loaded). Please upload via the scan page instead."}), 503

    try:
        # Decode base64 image
        image_data = data["image"]
        if "," in image_data:
            image_data = image_data.split(",")[1]

        img_bytes = base64.b64decode(image_data)
        img = Image.open(BytesIO(img_bytes)).convert("RGB")

        # Save temporarily
        upload_dir = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_dir, exist_ok=True)
        temp_name = f"camera_{uuid.uuid4().hex}.jpg"
        temp_path = os.path.join(upload_dir, temp_name)
        img.save(temp_path)

        # Run detection
        detector = get_detector()
        result = detector.predict(temp_path)

        # Generate heatmap
        heatmap_name = f"heatmap_{temp_name}"
        heatmap_path = os.path.join(upload_dir, heatmap_name)
        try:
            generate_gradcam(detector.get_model(), temp_path, heatmap_path)
        except Exception:
            heatmap_name = ""

        body_part = data.get("body_part", "Unknown")

        # Get suggestions if fracture detected
        recovery = ""
        doctor_rec = ""
        specialists = []
        if result["fracture_detected"]:
            recovery = get_recovery_suggestions(result["severity"], result["fracture_type"], body_part)
            doctor_rec = get_doctor_recommendation(result["severity"], result["fracture_type"], body_part)
            specialists = get_specialists_list(result["severity"], result["fracture_type"], body_part)

        # Save to database
        scan = Scan(
            user_id=current_user.id,
            original_image=temp_name,
            heatmap_image=heatmap_name,
            fracture_detected=result["fracture_detected"],
            confidence=result["confidence"],
            severity=result["severity"],
            fracture_type=result["fracture_type"],
            recovery_suggestion=recovery,
            doctor_recommendation=doctor_rec,
            body_part=body_part,
            notes="Captured via live camera",
        )
        db.session.add(scan)
        db.session.commit()

        return jsonify({
            "success": True,
            "scan_id": scan.id,
            "fracture_detected": result["fracture_detected"],
            "confidence": round(result["confidence"] * 100, 2),
            "severity": result["severity"],
            "fracture_type": result["fracture_type"],
            "heatmap_url": f"/uploads/{heatmap_name}" if heatmap_name else "",
            "original_url": f"/uploads/{temp_name}",
            "recovery": recovery,
            "specialists": specialists,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/voice-command", methods=["POST"])
@login_required
def voice_command():
    """
    Process voice commands from the speech-to-text system.

    Request JSON:
        {"command": "scan my xray"}

    Returns:
        JSON with action to perform
    """
    data = request.get_json()
    if not data or "command" not in data:
        return jsonify({"error": "No command received"}), 400

    command = data["command"].lower().strip()

    # ── Command Mapping ──
    actions = {
        "scan": {"action": "navigate", "url": "/scan", "message": "Opening scan page..."},
        "upload": {"action": "navigate", "url": "/scan", "message": "Opening upload page..."},
        "dashboard": {"action": "navigate", "url": "/dashboard", "message": "Opening dashboard..."},
        "history": {"action": "navigate", "url": "/dashboard", "message": "Opening patient history..."},
        "home": {"action": "navigate", "url": "/", "message": "Going to home page..."},
        "logout": {"action": "navigate", "url": "/logout", "message": "Logging out..."},
        "camera": {"action": "open_camera", "message": "Starting camera scanner..."},
        "report": {"action": "navigate", "url": "/dashboard", "message": "Opening reports..."},
        "help": {"action": "show_help", "message": "Available commands: scan, upload, dashboard, history, camera, report, home, logout, help"},
    }

    # Find matching action
    for keyword, action_data in actions.items():
        if keyword in command:
            return jsonify({"success": True, **action_data})

    return jsonify({
        "success": True,
        "action": "unknown",
        "message": f"Command not recognized: '{command}'. Say 'help' for available commands."
    })


@api_bp.route("/scan-history", methods=["GET"])
@login_required
def scan_history():
    """
    Get all scan history for the current user.
    Returns paginated results as JSON.
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    scans = Scan.query.filter_by(user_id=current_user.id)\
                      .order_by(Scan.scanned_at.desc())\
                      .paginate(page=page, per_page=per_page)

    return jsonify({
        "scans": [s.to_dict() for s in scans.items],
        "total": scans.total,
        "pages": scans.pages,
        "current_page": scans.page,
    })


@api_bp.route("/delete-scan/<int:scan_id>", methods=["DELETE"])
@login_required
def delete_scan(scan_id):
    """Delete a scan record and associated files."""
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first()
    if not scan:
        return jsonify({"error": "Scan not found"}), 404

    # Delete files
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    report_dir = current_app.config["REPORT_FOLDER"]

    for filename in [scan.original_image, scan.heatmap_image]:
        if filename:
            path = os.path.join(upload_dir, filename)
            if os.path.exists(path):
                os.remove(path)

    if scan.report_path:
        path = os.path.join(report_dir, scan.report_path)
        if os.path.exists(path):
            os.remove(path)

    db.session.delete(scan)
    db.session.commit()

    return jsonify({"success": True, "message": "Scan deleted successfully"})
