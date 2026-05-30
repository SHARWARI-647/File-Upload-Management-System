"""Admin blueprint: manage users and all files."""

import os

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from extensions import db
from models import ActivityLog, FileRecord, User
from utils import format_file_size, log_activity, resolve_file_path

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    """Decorator ensuring current user is admin."""
    from functools import wraps

    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated


@admin_bp.route("/")
@admin_required
def index():
    total_users = User.query.count()
    total_files = FileRecord.query.count()
    total_size = db.session.query(func.coalesce(func.sum(FileRecord.file_size), 0)).scalar()
    total_downloads = db.session.query(func.coalesce(func.sum(FileRecord.download_count), 0)).scalar()

    users = User.query.order_by(User.created_at.desc()).all()
    all_files = FileRecord.query.order_by(FileRecord.upload_date.desc()).limit(50).all()
    recent_logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(20).all()

    stats = {
        "total_users": total_users,
        "total_files": total_files,
        "total_size": format_file_size(total_size),
        "total_downloads": total_downloads,
    }

    return render_template(
        "admin.html",
        stats=stats,
        users=users,
        all_files=all_files,
        recent_logs=recent_logs,
        format_file_size=format_file_size,
    )


@admin_bp.route("/users/<int:user_id>/toggle-admin", methods=["POST"])
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot change your own admin status.", "danger")
        return redirect(url_for("admin.index"))

    user.is_admin = not user.is_admin
    db.session.commit()
    log_activity(current_user.id, "admin_toggle", f"Toggled admin for {user.username}")
    flash(f"Admin status updated for {user.username}.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("admin.index"))

    username = user.username
    for f in user.files:
        path = resolve_file_path(f)
        if path and os.path.isfile(path):
            os.remove(path)

    db.session.delete(user)
    db.session.commit()
    log_activity(current_user.id, "admin_delete_user", f"Deleted user {username}")
    flash(f"User {username} deleted.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/files/<int:file_id>/delete", methods=["POST"])
@admin_required
def delete_file(file_id):
    record = FileRecord.query.get_or_404(file_id)
    path = resolve_file_path(record)
    if path and os.path.isfile(path):
        os.remove(path)

    name = record.original_filename
    db.session.delete(record)
    db.session.commit()
    log_activity(current_user.id, "admin_delete_file", f"Admin deleted {name}")
    flash(f'File "{name}" deleted.', "success")
    return redirect(url_for("admin.index"))
