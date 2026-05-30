"""File management blueprint: upload, list, download, delete, rename, share, preview."""

import os

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from extensions import db
from models import ActivityLog, FileRecord
from utils import (
    allowed_file,
    format_file_size,
    generate_share_token,
    generate_stored_filename,
    get_extension,
    is_previewable,
    log_activity,
    resolve_file_path,
    user_upload_path,
)

files_bp = Blueprint("files", __name__, url_prefix="/files")


def _get_user_file(file_id: int) -> FileRecord:
    record = FileRecord.query.get_or_404(file_id)
    if record.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return record


@files_bp.route("/")
@login_required
def list_files():
    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "date")
    order = request.args.get("order", "desc")

    query = FileRecord.query.filter_by(user_id=current_user.id)

    if search:
        query = query.filter(FileRecord.original_filename.ilike(f"%{search}%"))

    sort_map = {
        "date": FileRecord.upload_date,
        "size": FileRecord.file_size,
        "type": FileRecord.file_type,
        "name": FileRecord.original_filename,
    }
    sort_col = sort_map.get(sort, FileRecord.upload_date)
    query = query.order_by(sort_col.desc() if order == "desc" else sort_col.asc())

    files = query.all()
    return render_template(
        "files.html",
        files=files,
        search=search,
        sort=sort,
        order=order,
        format_file_size=format_file_size,
        is_previewable=is_previewable,
    )


@files_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file part."}), 400

    uploaded = request.files["file"]
    if not uploaded or not uploaded.filename:
        return jsonify({"success": False, "message": "No file selected."}), 400

    original = secure_filename(uploaded.filename)
    if not original:
        return jsonify({"success": False, "message": "Invalid filename."}), 400

    if not allowed_file(original):
        return jsonify({"success": False, "message": "File type not allowed."}), 400

    stored_name = generate_stored_filename(original)
    user_dir = user_upload_path(current_user.id)
    full_path = os.path.join(user_dir, stored_name)

    uploaded.save(full_path)
    file_size = os.path.getsize(full_path)
    ext = get_extension(original)

    record = FileRecord(
        user_id=current_user.id,
        original_filename=original,
        stored_filename=stored_name,
        file_path=full_path,
        file_size=file_size,
        file_type=ext,
    )
    db.session.add(record)
    db.session.commit()
    log_activity(current_user.id, "upload", f"Uploaded {original}", record.id)

    return jsonify(
        {
            "success": True,
            "message": "File uploaded successfully.",
            "file": {
                "id": record.id,
                "name": record.original_filename,
                "size": format_file_size(record.file_size),
                "type": record.file_type,
            },
        }
    )


@files_bp.route("/download/<int:file_id>")
@login_required
def download(file_id):
    record = _get_user_file(file_id)
    path = resolve_file_path(record)
    if not path or not os.path.isfile(path):
        abort(404)

    record.download_count += 1
    db.session.commit()
    log_activity(current_user.id, "download", f"Downloaded {record.original_filename}", record.id)

    return send_file(path, as_attachment=True, download_name=record.original_filename)


@files_bp.route("/delete/<int:file_id>", methods=["POST"])
@login_required
def delete(file_id):
    record = _get_user_file(file_id)
    path = resolve_file_path(record)
    if path and os.path.isfile(path):
        os.remove(path)

    name = record.original_filename
    db.session.delete(record)
    db.session.commit()
    log_activity(current_user.id, "delete", f"Deleted {name}")

    flash(f'"{name}" deleted.', "success")
    return redirect(url_for("files.list_files"))


@files_bp.route("/rename/<int:file_id>", methods=["POST"])
@login_required
def rename(file_id):
    record = _get_user_file(file_id)
    new_name = secure_filename(request.form.get("new_name", "").strip())
    if not new_name:
        flash("Invalid filename.", "danger")
        return redirect(url_for("files.list_files"))

    ext = get_extension(record.original_filename)
    if not new_name.lower().endswith(f".{ext}"):
        new_name = f"{new_name}.{ext}"

    old_name = record.original_filename
    record.original_filename = new_name
    db.session.commit()
    log_activity(current_user.id, "rename", f"Renamed {old_name} to {new_name}", record.id)
    flash("File renamed.", "success")
    return redirect(url_for("files.list_files"))


@files_bp.route("/share/<int:file_id>", methods=["POST"])
@login_required
def share(file_id):
    record = _get_user_file(file_id)
    if not record.share_token:
        record.share_token = generate_share_token()
    record.share_enabled = True
    db.session.commit()
    log_activity(current_user.id, "share", f"Share link created for {record.original_filename}", record.id)

    share_url = url_for("files.public_download", token=record.share_token, _external=True)
    return jsonify({"success": True, "url": share_url})


@files_bp.route("/unshare/<int:file_id>", methods=["POST"])
@login_required
def unshare(file_id):
    record = _get_user_file(file_id)
    record.share_enabled = False
    db.session.commit()
    flash("Share link disabled.", "info")
    return redirect(url_for("files.list_files"))


@files_bp.route("/preview/<int:file_id>")
@login_required
def preview(file_id):
    record = _get_user_file(file_id)
    if not is_previewable(record.file_type):
        abort(400, "Preview not available for this file type.")

    path = resolve_file_path(record)
    if not path or not os.path.isfile(path):
        abort(404)

    mimetype = "application/pdf" if record.file_type == "pdf" else f"image/{record.file_type}"
    return send_file(path, mimetype=mimetype)


@files_bp.route("/public/<token>")
def public_download(token):
    """Public download via share link (no login required)."""
    record = FileRecord.query.filter_by(share_token=token, share_enabled=True).first_or_404()
    path = resolve_file_path(record)
    if not path or not os.path.isfile(path):
        abort(404)

    record.download_count += 1
    db.session.commit()
    log_activity(record.user_id, "share_download", f"Shared download: {record.original_filename}", record.id)

    return send_file(path, as_attachment=True, download_name=record.original_filename)


@files_bp.route("/history")
@login_required
def history():
    logs = (
        ActivityLog.query.filter_by(user_id=current_user.id)
        .filter(ActivityLog.action.in_(["upload", "download", "delete", "rename", "share"]))
        .order_by(ActivityLog.created_at.desc())
        .limit(50)
        .all()
    )
    return render_template("history.html", logs=logs)
