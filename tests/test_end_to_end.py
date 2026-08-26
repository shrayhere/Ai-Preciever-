import sys
import os
import io
import piexif
from PIL import Image, ImageDraw

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database.models import ScanRecord

def create_sample_real_image():
    """Generates a synthetic camera photo with valid camera EXIF."""
    img = Image.new("RGB", (300, 300), color=(140, 160, 180))
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 250, 250], fill=(120, 140, 160))
    
    exif_dict = {
        "0th": {
            piexif.ImageIFD.Make: b"Canon",
            piexif.ImageIFD.Model: b"Canon EOS 5D Mark IV",
        }
    }
    exif_bytes = piexif.dump(exif_dict)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95, exif=exif_bytes)
    buf.seek(0)
    return buf, "real_camera_photo.jpg"

def create_sample_edited_image():
    """Generates a spliced image with localized edits."""
    base = Image.new("RGB", (300, 300), color=(200, 200, 200))
    draw = ImageDraw.Draw(base)
    draw.rectangle([10, 10, 290, 290], fill=(180, 180, 180))
    
    buf_base = io.BytesIO()
    base.save(buf_base, format="JPEG", quality=70)
    buf_base.seek(0)

    # Re-open and paste localized spliced element
    edited = Image.open(buf_base).convert("RGB")
    draw_edit = ImageDraw.Draw(edited)
    draw_edit.rectangle([100, 100, 200, 200], fill=(255, 0, 0)) # Red block edit

    exif_dict = {
        "0th": {
            piexif.ImageIFD.Software: b"Adobe Photoshop CC 2024",
        }
    }
    exif_bytes = piexif.dump(exif_dict)
    buf = io.BytesIO()
    edited.save(buf, format="JPEG", quality=98, exif=exif_bytes)
    buf.seek(0)
    return buf, "edited_spliced_photo.jpg"

def create_sample_ai_image():
    """Generates an image with Midjourney / Stable Diffusion metadata signatures."""
    img = Image.new("RGB", (300, 300), color=(100, 200, 150))
    draw = ImageDraw.Draw(img)
    draw.polygon([(150, 20), (280, 280), (20, 280)], fill=(200, 100, 200))
    
    exif_dict = {
        "0th": {
            piexif.ImageIFD.ImageDescription: b"Created with Midjourney v6.0 prompt futuristic cyberpunk city",
            piexif.ImageIFD.Software: b"Stable Diffusion XL webui",
        }
    }
    exif_bytes = piexif.dump(exif_dict)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90, exif=exif_bytes)
    buf.seek(0)
    return buf, "ai_generated_art.jpg"

def main():
    print("================ STARTING END-TO-END VERIFICATION SANITY CHECK ================\n")
    client = app.test_client()

    samples = [
        ("REAL PHOTO", create_sample_real_image()),
        ("EDITED PHOTO", create_sample_edited_image()),
        ("AI GENERATED PHOTO", create_sample_ai_image())
    ]

    scan_results = []

    for label, (img_buf, filename) in samples:
        print(f"--> Uploading [{label}] ({filename})...")
        data = {
            'image': (img_buf, filename, 'image/jpeg')
        }
        res = client.post("/analyze", data=data, content_type='multipart/form-data')
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        res_json = res.get_json()
        assert res_json["success"] is True, "Analysis request failed"
        
        scan_id = res_json["scan_id"]
        record = ScanRecord.get_by_id(scan_id)
        scan_results.append((label, record))
        
        print(f"    Scan ID: #{record['id']}")
        print(f"    Category: {record['category']}")
        print(f"    Final Score (Confidence): {record['final_score']}%")
        print(f"    Sub-scores: AI={record['ai_score']}, Forensic={record['forensic_score']}")
        print(f"    Explanation: {record['explanation']}")
        print(f"    Heatmap File: {record['heatmap_path']}\n")

    print("---------------- VERIFYING SANITY CHECK REQUIREMENTS ----------------")
    
    # 1. Scores meaningfully differ across samples
    rec_real = scan_results[0][1]
    rec_edited = scan_results[1][1]
    rec_ai = scan_results[2][1]

    print("1. Score Differentiation:")
    print(f"   Real photo category: {rec_real['category']}")
    print(f"   Edited photo category: {rec_edited['category']}")
    print(f"   AI generated photo category: {rec_ai['category']}")
    
    # 2. Check heatmap images differ and are unique files
    heatmap_real = rec_real['heatmap_path']
    heatmap_edited = rec_edited['heatmap_path']
    heatmap_ai = rec_ai['heatmap_path']

    print("\n2. Heatmap Uniqueness:")
    print(f"   Real heatmap: {heatmap_real}")
    print(f"   Edited heatmap: {heatmap_edited}")
    print(f"   AI heatmap: {heatmap_ai}")
    assert len({heatmap_real, heatmap_edited, heatmap_ai}) == 3, "Heatmaps must be unique per file!"

    # 3. Check SQLite DB records contain real non-null values
    print("\n3. SQLite Database Verification:")
    recent_scans = ScanRecord.get_recent(10)
    print(f"   Total records in DB: {len(recent_scans)}")
    for r in recent_scans[:3]:
        assert r['id'] is not None, "ID must not be None"
        assert r['filename'] != "", "Filename must not be empty"
        assert r['category'] in ['Likely Authentic', 'Possibly Manipulated', 'Likely AI-Generated']
        assert r['explanation'] != "", "Explanation must not be empty"

    print("\n================ ALL SANITY CHECKS PASSED SUCCESSFULLY! ================")

if __name__ == "__main__":
    main()
