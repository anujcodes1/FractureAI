"""
FractureAI Configuration
========================
All application settings and environment configuration.
"""

import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class."""

    # Flask secret key for session management
    SECRET_KEY = os.environ.get("SECRET_KEY", "fractureai-secret-key-2026")

    # SQLite database path
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'fractureai.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    REPORT_FOLDER = os.path.join(BASE_DIR, "reports")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "dcm"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload

    # Email settings (configure with your SMTP server)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@fractureai.com")

    # AI Model settings
    MODEL_PATH = os.path.join(BASE_DIR, "models", "fracture_cnn.h5")
    IMAGE_SIZE = (224, 224)  # Input size for CNN

    # Fracture severity thresholds
    SEVERITY_LOW = 0.3
    SEVERITY_MEDIUM = 0.6
    # Above 0.6 = High severity
