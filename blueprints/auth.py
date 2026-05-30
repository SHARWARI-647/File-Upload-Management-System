"""Authentication blueprint: register, login, logout."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from extensions import db
from models import User
from utils import log_activity

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        full_name = request.form.get("full_name", "").strip()

        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if not email or "@" not in email:
            errors.append("Valid email is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if User.query.filter_by(username=username).first():
            errors.append("Username already taken.")
        if User.query.filter_by(email=email).first():
            errors.append("Email already registered.")

        if errors:
            for msg in errors:
                flash(msg, "danger")
            return render_template("register.html")

        user = User(username=username, email=email, full_name=full_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        log_activity(user.id, "register", f"Account created: {username}")
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            log_activity(user.id, "login", "User logged in")
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            if user.is_admin:
                return redirect(url_for("admin.index"))
            return redirect(url_for("dashboard.index"))

        flash("Invalid username/email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        log_activity(current_user.id, "logout", "User logged out")
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
