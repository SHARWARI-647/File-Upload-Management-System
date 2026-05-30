"""User profile blueprint: view profile, update info, change password."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import User
from utils import log_activity

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/")
@login_required
def index():
    return render_template("profile.html", user=current_user)


@profile_bp.route("/update", methods=["POST"])
@login_required
def update():
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    username = request.form.get("username", "").strip()

    if len(username) < 3:
        flash("Username must be at least 3 characters.", "danger")
        return redirect(url_for("profile.index"))

    existing = User.query.filter(User.email == email, User.id != current_user.id).first()
    if existing:
        flash("Email already in use.", "danger")
        return redirect(url_for("profile.index"))

    existing = User.query.filter(User.username == username, User.id != current_user.id).first()
    if existing:
        flash("Username already taken.", "danger")
        return redirect(url_for("profile.index"))

    current_user.full_name = full_name
    current_user.email = email
    current_user.username = username
    db.session.commit()
    log_activity(current_user.id, "profile_update", "Profile information updated")
    flash("Profile updated successfully.", "success")
    return redirect(url_for("profile.index"))


@profile_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    current_pw = request.form.get("current_password", "")
    new_pw = request.form.get("new_password", "")
    confirm = request.form.get("confirm_password", "")

    if not current_user.check_password(current_pw):
        flash("Current password is incorrect.", "danger")
        return redirect(url_for("profile.index"))

    if len(new_pw) < 6:
        flash("New password must be at least 6 characters.", "danger")
        return redirect(url_for("profile.index"))

    if new_pw != confirm:
        flash("New passwords do not match.", "danger")
        return redirect(url_for("profile.index"))

    current_user.set_password(new_pw)
    db.session.commit()
    log_activity(current_user.id, "password_change", "Password changed")
    flash("Password changed successfully.", "success")
    return redirect(url_for("profile.index"))
