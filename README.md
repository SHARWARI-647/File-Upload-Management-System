# File Upload & Management Web Application

A full-featured file manager built with **Flask**, **SQLite**, **SQLAlchemy**, **Bootstrap 5**, and **JavaScript**. Users can register, upload files via drag-and-drop, manage their library, and share files via public links. Admins can manage all users and files.

## Features

- User registration, login, logout with Werkzeug password hashing
- Responsive dashboard with sidebar, stats cards, and recent activity
- Drag-and-drop uploads with progress bar (max 20 MB)
- File types: PDF, DOCX, PPTX, XLSX, JPG, PNG, ZIP
- Search, sort, download, delete, rename
- Image and PDF preview
- Share links with download counter
- Upload history and activity logs
- User profile and password change
- Admin dashboard for users and files
- Dark / light theme toggle
- CSRF protection and secure file handling

## Project Structure

```
file_manager/
├── app.py                 # Application factory & entry point
├── models.py              # SQLAlchemy models
├── config.py              # Configuration
├── extensions.py          # Flask extensions
├── utils.py               # Helpers
├── requirements.txt
├── blueprints/            # Route modules (MVC controllers)
├── templates/             # Jinja2 views
├── static/                # CSS, JS, uploads
└── database/              # SQLite database
```

## Quick Start (Local)

1. **Clone and enter the project**

   ```bash
   cd file_manager
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate    # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**

   ```bash
   copy .env.example .env    # Windows
   # cp .env.example .env    # macOS/Linux
   ```

   Edit `.env` and set a strong `SECRET_KEY` and `ADMIN_PASSWORD`.

5. **Run the application**

   ```bash
   python app.py
   ```

6. **Open in browser**

   - URL: http://127.0.0.1:5000
   - Default admin: `admin` / password from `ADMIN_PASSWORD` in `.env` (default: `admin123`)

## Default Admin

On first startup, an admin user is created if none exists:

| Field    | Default                    |
|----------|----------------------------|
| Username | `admin`                    |
| Email    | `ADMIN_EMAIL` from `.env`  |
| Password | `ADMIN_PASSWORD` from `.env` |

**Change the default password immediately in production.**

## Deploy on Render

1. Push this project to GitHub.
2. Create a new **Web Service** on [Render](https://render.com).
3. Connect your repository.
4. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Add environment variables:
   - `FLASK_ENV=production`
   - `SECRET_KEY` (auto-generate or set manually)
   - `ADMIN_EMAIL`, `ADMIN_PASSWORD`
6. Optional: attach a **disk** mounted at `database/` for SQLite persistence (see `render.yaml`).

Alternatively, use the included `render.yaml` Blueprint for one-click deploy.

## Security Notes

- Files are stored per-user under `static/uploads/<user_id>/`
- Path traversal is blocked via `safe_join`
- File extensions are validated server-side
- CSRF tokens required on forms and AJAX requests
- Use HTTPS in production (`SESSION_COOKIE_SECURE=true`)

## Tech Stack

- Python 3.11+
- Flask 3, Flask-Login, Flask-WTF, SQLAlchemy
- SQLite
- Bootstrap 5, Bootstrap Icons
- Vanilla JavaScript (XHR upload, theme toggle)

## License

MIT
