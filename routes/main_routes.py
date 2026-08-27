import os
import uuid
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_from_directory, current_app
from werkzeug.utils import secure_filename
from PIL import Image

from config import Config
from detectors.ai_detector import AIDetector
from detectors.forensics_detector import ForensicsDetector
from detectors.metadata_detector import MetadataDetector
from scoring.scorer import AuthenticityScorer
from database.models import ScanRecord

main_bp = Blueprint("main", __name__)

# Initialize detectors (lazy load inside detectors)
ai_detector = AIDetector()
forensics_detector = ForensicsDetector()
metadata_detector = MetadataDetector()
scorer = AuthenticityScorer()

def validate_image_file(file):
    """Validates filename extension, MIME type, and verifies image integrity with Pillow."""
    if not file or file.filename == '':
        return False, "No file selected."
    
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in Config.ALLOWED_EXTENSIONS:
        return False, f"Invalid file extension '.{ext}'. Allowed formats: JPG, JPEG, PNG."
    
    # Header MIME-type check
    if file.mimetype and file.mimetype.lower() not in Config.ALLOWED_MIMETYPES:
        return False, f"Invalid MIME type '{file.mimetype}'. File must be a valid JPEG or PNG image."
    
    # Deep verification using PIL
    try:
        file.seek(0)
        img = Image.open(file.stream)
        img.verify()
        file.seek(0)
        if img.format and img.format.lower() not in ['jpeg', 'png']:
            return False, f"Unsupported image format: {img.format}"
    except Exception as e:
        return False, f"File verification failed: {str(e)}"
    
    return True, "Valid"

@main_bp.route("/")
def index():
    recent_scans = ScanRecord.get_recent(limit=7)
    return render_template("index.html", recent_scans=recent_scans)

@main_bp.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image file provided."}), 400
    
    file = request.files["image"]
    is_valid, err_msg = validate_image_file(file)
    if not is_valid:
        return jsonify({"success": False, "error": err_msg}), 400

    # Sanitize and assign UUID-based unique filename
    orig_name = secure_filename(file.filename)
    ext = orig_name.rsplit('.', 1)[-1].lower() if '.' in orig_name else 'jpg'
    unique_filename = f"{uuid.uuid4().hex}_{orig_name}"
    save_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
    
    file.save(save_path)

    try:
        # Run detection pipeline
        ai_res = ai_detector.analyze(save_path)
        forensic_res = forensics_detector.analyze(save_path, output_heatmap_dir=Config.UPLOAD_FOLDER)
        metadata_res = metadata_detector.analyze(save_path)

        # Compute combined score
        final_res = scorer.evaluate(ai_res, forensic_res, metadata_res)

        # Save to SQLite database
        scan_id = ScanRecord.create(
            filename=unique_filename,
            ai_score=final_res["sub_scores"]["ai_score"],
            forensic_score=final_res["sub_scores"]["forensic_score"],
            metadata_flags=final_res["metadata_flags"],
            final_score=final_res["confidence_score"],
            category=final_res["category"],
            explanation=final_res["explanation"],
            heatmap_path=final_res["heatmap_path"]
        )

        return jsonify({
            "success": True,
            "scan_id": scan_id,
            "redirect_url": url_for("main.results", scan_id=scan_id)
        })

    except Exception as e:
        current_app.logger.error(f"Error during analysis: {e}")
        return jsonify({"success": False, "error": f"Analysis failed: {str(e)}"}), 500

@main_bp.route("/results/<int:scan_id>")
def results(scan_id):
    scan = ScanRecord.get_by_id(scan_id)
    if not scan:
        flash("Scan record not found.", "error")
        return redirect(url_for("main.index"))
    
    return render_template("results.html", scan=scan)

@main_bp.route("/history")
def history():
    recent_scans = ScanRecord.get_recent(limit=7)
    return jsonify({"success": True, "scans": recent_scans})

@main_bp.route("/clear_history", methods=["POST"])
def clear_history():
    try:
        deleted_records = ScanRecord.delete_all()
        # Delete underlying uploaded image files and heatmaps from disk
        for rec in deleted_records:
            if rec.get("filename"):
                file_path = os.path.join(Config.UPLOAD_FOLDER, rec["filename"])
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        current_app.logger.warning(f"Failed to delete uploaded file {file_path}: {e}")
            if rec.get("heatmap_path"):
                heatmap_path = os.path.join(Config.UPLOAD_FOLDER, rec["heatmap_path"])
                if os.path.isfile(heatmap_path):
                    try:
                        os.remove(heatmap_path)
                    except Exception as e:
                        current_app.logger.warning(f"Failed to delete heatmap file {heatmap_path}: {e}")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({"success": True, "message": "Audit log history and stored images deleted successfully."})

        flash("Recent scan audit log and image data cleared successfully.", "success")
        return redirect(url_for("main.index"))
    except Exception as e:
        current_app.logger.error(f"Error clearing audit history: {e}")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({"success": False, "error": str(e)}), 500
        flash("Failed to clear audit history.", "error")
        return redirect(url_for("main.index"))

@main_bp.route("/uploads/<filename>")
def uploaded_file(filename):
    if os.path.isfile(os.path.join(Config.UPLOAD_FOLDER, filename)):
        return send_from_directory(Config.UPLOAD_FOLDER, filename)
    fallback_dir = os.path.join(Config.BASE_DIR, "static", "uploads")
    if os.path.isfile(os.path.join(fallback_dir, filename)):
        return send_from_directory(fallback_dir, filename)
    return "File not found", 404

