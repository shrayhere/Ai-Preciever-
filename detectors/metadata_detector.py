import os
import logging
from PIL import Image, ExifTags
from .base_detector import BaseDetector

logger = logging.getLogger(__name__)

EDITING_SOFTWARE_SIGNATURES = [
    "photoshop", "gimp", "lightroom", "paint.net", "photopea", 
    "affinity", "coreldraw", "canva", "pixlr", "snapseed"
]

AI_GENERATOR_SIGNATURES = [
    "chatgpt", "dall-e", "dalle", "midjourney", "stable diffusion", "stablediffusion",
    "comfyui", "automatic1111", "novelai", "firefly", "invokeai", "civitai", "bing_creator"
]

class MetadataDetector(BaseDetector):
    def analyze(self, image_path: str) -> dict:
        """
        Extracts EXIF metadata and filename signatures, checking for
        editing software or AI generator signatures.
        """
        try:
            filename = os.path.basename(image_path).lower()
            img = Image.open(image_path)
            exif_raw = img._getexif()

            exif_data = {}
            if exif_raw:
                for tag_id, value in exif_raw.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        try:
                            value = value.decode("utf-8", errors="ignore").strip('\x00')
                        except Exception:
                            value = str(value)
                    exif_data[str(tag)] = str(value)

            make = exif_data.get("Make", "").strip()
            model = exif_data.get("Model", "").strip()
            software = exif_data.get("Software", "").strip()
            image_desc = exif_data.get("ImageDescription", "").strip()
            user_comment = exif_data.get("UserComment", "").strip()

            all_text_metadata = f"{filename} {software} {image_desc} {user_comment}".lower()

            flags = []
            metadata_score = 0.0

            # 1. Check AI Generator signatures in EXIF and Filename
            ai_detected = [sig for sig in AI_GENERATOR_SIGNATURES if sig in all_text_metadata]
            if ai_detected:
                flags.append(f"AI generator signature detected in file metadata: {', '.join(ai_detected)}")
                metadata_score = max(metadata_score, 0.95)

            # 2. Check Editing Software signatures
            edit_detected = [sig for sig in EDITING_SOFTWARE_SIGNATURES if sig in all_text_metadata]
            if edit_detected:
                flags.append(f"Editing software signature detected: {', '.join(edit_detected)}")
                metadata_score = max(metadata_score, 0.6)

            # 3. Camera hardware verification
            has_camera = bool(make or model)
            if has_camera:
                flags.append(f"Camera metadata verified: {make} {model}".strip())
            elif not flags:
                if not exif_raw:
                    flags.append("EXIF camera metadata absent (common for web exports)")
                else:
                    flags.append("No editing or AI signatures found in metadata")

            return {
                "has_exif": bool(exif_raw),
                "metadata_score": round(metadata_score, 4),
                "camera_make": make or None,
                "camera_model": model or None,
                "software": software or None,
                "flags": flags,
                "raw_exif": exif_data,
                "status": "success"
            }

        except Exception as e:
            logger.warning(f"Error reading metadata for {image_path}: {e}")
            return {
                "has_exif": False,
                "metadata_score": 0.0,
                "camera_make": None,
                "camera_model": None,
                "software": None,
                "flags": ["Could not read metadata (standard image file)"],
                "raw_exif": {},
                "status": "warning"
            }
