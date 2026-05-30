"""SQLAlchemy database models."""

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    """Registered user account."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), default="")
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    files = db.relationship("FileRecord", backref="owner", lazy="dynamic", cascade="all, delete-orphan")
    activities = db.relationship("ActivityLog", backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class FileRecord(db.Model):
    """Metadata for an uploaded file."""

    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(32), nullable=False)
    upload_date = db.Column(db.DateTime, default=utcnow, index=True)
    download_count = db.Column(db.Integer, default=0)
    share_token = db.Column(db.String(64), unique=True, nullable=True, index=True)
    share_enabled = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<FileRecord {self.original_filename}>"


class ActivityLog(db.Model):
    """User activity and upload history."""

    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    action = db.Column(db.String(64), nullable=False)
    details = db.Column(db.String(512), default="")
    file_id = db.Column(db.Integer, db.ForeignKey("files.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)

    file = db.relationship("FileRecord", backref="activities", foreign_keys=[file_id])

    def __repr__(self):
        return f"<ActivityLog {self.action}>"
