"""
FractureAI — Main Application
================================
AI-Powered Bone Fracture Detection System

This is the main entry point for the Flask application.
It initializes all components: database, login manager,
blueprints, and serves static files.

Usage:
    python app.py

Author: FractureAI Team
Version: 2.0 (2026)
"""

import os
from flask import Flask, render_template, send_from_directory
from flask_login import LoginManager

from config import Config
from database.db import db, User
from utils.email_service import mail


def create_app():
    """
    Application factory pattern.
    Creates and configures the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── Create necessary directories ──
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["REPORT_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    # ── Initialize Extensions ──
    db.init_app(app)
    mail.init_app(app)

    # ── Login Manager Setup ──
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this feature."
    login_manager.login_message_category = "info"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for session management."""
        return User.query.get(int(user_id))

    # ── Register Blueprints ──
    from routes.auth import auth_bp
    from routes.scan import scan_bp
    from routes.dashboard import dashboard_bp
    from routes.api import api_bp
    from routes.features import features_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(scan_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(features_bp)

    # ── Main Routes ──
    @app.route("/")
    def index():
        """Landing page."""
        return render_template("index.html")

    # ── Serve Uploaded Files ──
    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        """Serve uploaded images (X-rays and heatmaps)."""
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # ── Error Handlers ──
    @app.errorhandler(404)
    def not_found(e):
        return render_template("base.html", error="Page not found"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("base.html", error="Internal server error"), 500

    # ── Create Database Tables ──
    with app.app_context():
        db.create_all()
        print("[FractureAI] Database initialized")

    return app


# ── Run the Application ──
if __name__ == "__main__":
    app = create_app()
    print("\n" + "=" * 55)
    print("  FractureAI - Bone Fracture Detection System")
    print("  Running at: http://127.0.0.1:5000")
    print("  Upload folder:", app.config["UPLOAD_FOLDER"])
    print("=" * 55 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
