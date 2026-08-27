import os
import tempfile

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def get_writable_upload_folder():
    local_upload_dir = os.path.join(BASE_DIR, "static", "uploads")
    try:
        os.makedirs(local_upload_dir, exist_ok=True)
        test_file = os.path.join(local_upload_dir, ".write_test")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return local_upload_dir
    except Exception:
        tmp_upload_dir = os.path.join(tempfile.gettempdir(), "deepverify_uploads")
        try:
            os.makedirs(tmp_upload_dir, exist_ok=True)
        except Exception:
            pass
        return tmp_upload_dir

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "deepverify-secret-key-super-secure")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB limit
    BASE_DIR = BASE_DIR
    UPLOAD_FOLDER = get_writable_upload_folder()
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
    ALLOWED_MIMETYPES = {"image/jpeg", "image/png", "image/pjpeg", "image/x-png"}

