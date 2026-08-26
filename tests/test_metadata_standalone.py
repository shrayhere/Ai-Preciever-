import sys
import os
from PIL import Image
import piexif

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from detectors.metadata_detector import MetadataDetector

def main():
    test_dir = os.path.dirname(__file__)
    
    # 1. Plain image (no EXIF)
    no_exif_path = os.path.join(test_dir, "sample_no_exif.jpg")
    img1 = Image.new("RGB", (100, 100), color=(100, 100, 100))
    img1.save(no_exif_path, "JPEG")

    # 2. Image with EXIF metadata (Photoshop tag)
    exif_path = os.path.join(test_dir, "sample_with_exif.jpg")
    img2 = Image.new("RGB", (100, 100), color=(150, 150, 150))
    
    exif_dict = {
        "0th": {
            piexif.ImageIFD.Make: b"Canon",
            piexif.ImageIFD.Model: b"Canon EOS 80D",
            piexif.ImageIFD.Software: b"Adobe Photoshop CC 2024 (Windows)",
        }
    }
    exif_bytes = piexif.dump(exif_dict)
    img2.save(exif_path, "JPEG", exif=exif_bytes)

    detector = MetadataDetector()

    print("--- Test 1: No EXIF ---")
    res1 = detector.analyze(no_exif_path)
    print(res1)

    print("\n--- Test 2: With EXIF (Photoshop) ---")
    res2 = detector.analyze(exif_path)
    print(res2)

if __name__ == "__main__":
    main()
