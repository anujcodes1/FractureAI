"""
FractureAI Database Models
===========================
SQLAlchemy models for Users, Scans, and Patient History.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize SQLAlchemy instance (shared across the app)
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    User model for authentication.
    Stores user credentials and profile information.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(150), default="")
    role = db.Column(db.String(20), default="patient")  # patient / doctor
    language = db.Column(db.String(10), default="en")  # en / hi
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: one user has many scans
    scans = db.relationship("Scan", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Scan(db.Model):
    """
    Scan model for storing X-ray analysis results.
    Each scan contains the uploaded image, AI predictions, and report path.
    """
    __tablename__ = "scans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Image paths
    original_image = db.Column(db.String(300), nullable=False)  # Uploaded X-ray
    heatmap_image = db.Column(db.String(300), default="")  # Grad-CAM heatmap

    # AI Predictions
    fracture_detected = db.Column(db.Boolean, default=False)
    confidence = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    severity = db.Column(db.String(20), default="N/A")  # Low / Medium / High
    fracture_type = db.Column(db.String(100), default="N/A")

    # Recovery & Suggestions
    recovery_suggestion = db.Column(db.Text, default="")
    doctor_recommendation = db.Column(db.Text, default="")

    # Report
    report_path = db.Column(db.String(300), default="")

    # Metadata
    body_part = db.Column(db.String(50), default="Unknown")
    notes = db.Column(db.Text, default="")
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Scan {self.id} - {'Fracture' if self.fracture_detected else 'Normal'}>"

    def to_dict(self):
        """Convert scan to dictionary for API responses."""
        return {
            "id": self.id,
            "fracture_detected": self.fracture_detected,
            "confidence": round(self.confidence * 100, 2),
            "severity": self.severity,
            "fracture_type": self.fracture_type,
            "recovery_suggestion": self.recovery_suggestion,
            "doctor_recommendation": self.doctor_recommendation,
            "body_part": self.body_part,
            "scanned_at": self.scanned_at.strftime("%Y-%m-%d %H:%M"),
            "original_image": self.original_image,
            "heatmap_image": self.heatmap_image,
        }


class Appointment(db.Model):
    """
    Appointment model for doctor appointment booking.
    Stores appointment details and status.
    """
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Clinic / Doctor info
    clinic_name = db.Column(db.String(200), nullable=False)
    clinic_address = db.Column(db.String(500), default="")
    doctor_name = db.Column(db.String(150), default="To be assigned")

    # Appointment details
    appointment_date = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(300), default="Orthopedic Consultation")
    notes = db.Column(db.Text, default="")

    # Status: confirmed / cancelled / completed
    status = db.Column(db.String(20), default="confirmed")

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship("User", backref=db.backref("appointments", lazy=True))

    def __repr__(self):
        return f"<Appointment {self.id} - {self.clinic_name} on {self.appointment_date}>"
