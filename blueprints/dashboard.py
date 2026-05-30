"""Dashboard blueprint: main user dashboard."""

from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy import func

from extensions import db
from models import ActivityLog, FileRecord
from utils import format_file_size

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    user_files = FileRecord.query.filter_by(user_id=current_user.id)

    total_files = user_files.count()
    total_size = db.session.query(func.coalesce(func.sum(FileRecord.file_size), 0)).filter(
        FileRecord.user_id == current_user.id
    ).scalar()
    total_downloads = db.session.query(func.coalesce(func.sum(FileRecord.download_count), 0)).filter(
        FileRecord.user_id == current_user.id
    ).scalar()

    recent_files = (
        user_files.order_by(FileRecord.upload_date.desc()).limit(5).all()
    )
    recent_activity = (
        ActivityLog.query.filter_by(user_id=current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )

    stats = {
        "total_files": total_files,
        "total_size": format_file_size(total_size),
        "total_downloads": total_downloads,
    }

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_files=recent_files,
        recent_activity=recent_activity,
    )
