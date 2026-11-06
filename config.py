import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    """Application configuration settings."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "iitd-vlabs-smart-feedback-key-2026-prod-sec")
    
    # Upload Settings
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", str(BASE_DIR / "static" / "uploads"))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 25 * 1024 * 1024))  # 25 MB max total payload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    MAX_FILE_SIZE_MB = 10  # 10 MB per file limit

    # Database Configuration (MySQL credentials with SQLite automatic fallback)
    DB_TYPE = os.environ.get("DB_TYPE", "auto")  # 'mysql', 'sqlite', or 'auto'
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "iitd_feedback")
    
    # SQLite fallback file
    SQLITE_DB_PATH = os.environ.get("SQLITE_DB_PATH", str(BASE_DIR / "database" / "feedback.db"))

    # Admin Portal Credentials
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin@iitd2026")

    # Portal Metadata
    PORTAL_TITLE = "IIT Delhi Virtual Labs – Feedback Portal"
    INSTITUTE_NAME = "Indian Institute of Technology Delhi"
    PORTAL_VERSION = "2.4.0"

