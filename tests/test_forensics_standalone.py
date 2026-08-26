import sys
import os
from PIL import Image, ImageDraw

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from detectors.forensics_detector import ForensicsDetector

def main():
    test_dir = os.path.dirname(__file__)
    sample_path = os.path.join(test_dir, "sample_edited.jpg")
    output_dir = os.path.join(test_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # Create base image
    img = Image.new("RGB", (300, 300), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 250, 250], fill=(100, 150, 200))
    
    # Save base to JPG
    temp_jpg = os.path.join(test_dir, "temp_base.jpg")
    img.save(temp_jpg, "JPEG", quality=80)

    # Edit region (splicing/patch edit simulation)
    edited_img = Image.open(temp_jpg).convert("RGB")
    draw_edited = ImageDraw.Draw(edited_img)
    draw_edited.ellipse([100, 100, 180, 180], fill=(255, 50, 50))
    
    # Save edited image
    edited_img.save(sample_path, "JPEG", quality=95)
    print(f"Created simulated edited test image at {sample_path}")

    detector = ForensicsDetector()
    print("Analyzing test image with ForensicsDetector...")
    results = detector.analyze(sample_path, output_heatmap_dir=output_dir)
    print("Results:", results)

    heatmap_full_path = os.path.join(output_dir, results["heatmap_path"])
    print(f"Heatmap file exists: {os.path.exists(heatmap_full_path)} ({heatmap_full_path})")

if __name__ == "__main__":
    main()
