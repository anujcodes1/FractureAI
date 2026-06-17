"""
FractureAI Authentication Routes
==================================
Handles user registration, login, and logout.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import db, User

# Create auth blueprint
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Login page and authentication handler.
    GET: Render login form.
    POST: Validate credentials and log user in.
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for("scan.scan_page"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Find user by username
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            # Successful login
            login_user(user, remember=True)
            flash("Welcome back! Login successful.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("scan.scan_page"))
        else:
            flash("Invalid username or password. Please try again.", "error")

    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Registration page and user creation handler.
    GET: Render signup form.
    POST: Validate input and create new user.
    """
    if current_user.is_authenticated:
        return redirect(url_for("scan.scan_page"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        full_name = request.form.get("full_name", "").strip()

        # Validation
        errors = []
        if len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if "@" not in email:
            errors.append("Please enter a valid email address.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if User.query.filter_by(username=username).first():
            errors.append("Username already taken.")
        if User.query.filter_by(email=email).first():
            errors.append("Email already registered.")

        if errors:
            for err in errors:
                flash(err, "error")
        else:
            # Create new user
            new_user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                full_name=full_name or username,
            )
            db.session.add(new_user)
            db.session.commit()

            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("signup.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Log out the current user and redirect to home."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))
