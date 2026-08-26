import sys
import os
from PIL import Image, ImageDraw
import piexif

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from detectors.ai_detector import AIDetector
from detectors.forensics_detector import ForensicsDetector
from detectors.metadata_detector import MetadataDetector
from scoring.scorer import AuthenticityScorer

def main():
    test_dir = os.path.dirname(__file__)
    output_dir = os.path.join(test_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # Instantiate modules
    ai_det = AIDetector()
    forensic_det = ForensicsDetector()
    metadata_det = MetadataDetector()
    scorer = AuthenticityScorer()

    # Create a test image with Photoshop metadata and a localized edit circle
    test_img_path = os.path.join(test_dir, "sample_full_pipeline.jpg")
    img = Image.new("RGB", (300, 300), color=(180, 180, 180))
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 150, 150], fill=(50, 100, 150))

    exif_dict = {
        "0th": {
            piexif.ImageIFD.Make: b"Nikon",
            piexif.ImageIFD.Model: b"D850",
            piexif.ImageIFD.Software: b"Adobe Photoshop 2024",
        }
    }
    exif_bytes = piexif.dump(exif_dict)
    img.save(test_img_path, "JPEG", quality=90, exif=exif_bytes)

    print(f"Running full detector pipeline on {test_img_path}...")
    ai_res = ai_det.analyze(test_img_path)
    forensic_res = forensic_det.analyze(test_img_path, output_heatmap_dir=output_dir)
    metadata_res = metadata_det.analyze(test_img_path)

    final_result = scorer.evaluate(ai_res, forensic_res, metadata_res)

    print("\n================ FINAL SCORING OUTPUT ================")
    print(f"Category: {final_result['category']}")
    print(f"Confidence Score: {final_result['confidence_score']}%")
    print(f"Sub-scores: {final_result['sub_scores']}")
    print(f"Explanation: {final_result['explanation']}")
    print(f"Heatmap saved: {final_result['heatmap_path']}")
    print("======================================================")

if __name__ == "__main__":
    main()
