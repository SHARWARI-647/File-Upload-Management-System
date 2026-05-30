"""Utility helpers for file handling, security, and logging."""

import os
import secrets
import uuid
from pathlib import Path

from flask import current_app, request
from werkzeug.utils import secure_filename

from extensions import db
from models import ActivityLog


def allowed_file(filename: str) -> bool:
    """Check if extension is in the allow list."""
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""


def generate_stored_filename(original: str) -> str:
    """Create a unique stored name while preserving extension."""
    ext = get_extension(original)
    unique = uuid.uuid4().hex
    return f"{unique}.{ext}" if ext else unique


def user_upload_path(user_id: int) -> str:
    """Per-user upload directory to isolate files."""
    base = current_app.config["UPLOAD_FOLDER"]
    path = os.path.join(base, str(user_id))
    os.makedirs(path, exist_ok=True)
    return path


def safe_join(base: str, *paths: str) -> str | None:
    """Join paths and ensure result stays under base (prevent traversal)."""
    base = os.path.realpath(base)
    target = os.path.realpath(os.path.join(base, *paths))
    if os.path.commonpath([base, target]) != base:
        return None
    return target


def resolve_file_path(record) -> str | None:
    """Resolve absolute path for a file record with traversal protection."""
    upload_root = current_app.config["UPLOAD_FOLDER"]
    rel = os.path.relpath(record.file_path, upload_root)
    parts = rel.split(os.sep)
    return safe_join(upload_root, *parts)


def log_activity(user_id: int, action: str, details: str = "", file_id: int | None = None):
    """Persist an activity log entry."""
    entry = ActivityLog(
        user_id=user_id,
        action=action,
        details=details[:512],
        file_id=file_id,
    )
    db.session.add(entry)
    db.session.commit()


def generate_share_token() -> str:
    return secrets.token_urlsafe(32)


def format_file_size(size_bytes: int) -> str:
    """Human-readable file size."""
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}" if unit != "B" else f"{size_bytes} B"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def is_previewable(file_type: str) -> bool:
    return file_type in ("jpg", "jpeg", "png", "pdf")
