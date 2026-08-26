import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "deepverify-secret-key-super-secure")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB limit
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
    ALLOWED_MIMETYPES = {"image/jpeg", "image/png", "image/pjpeg", "image/x-png"}

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
