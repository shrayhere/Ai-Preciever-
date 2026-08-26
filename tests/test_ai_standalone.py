import sys
import os
from PIL import Image

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from detectors.ai_detector import AIDetector

def main():
    sample_path = os.path.join(os.path.dirname(__file__), "sample_test.jpg")
    img = Image.new("RGB", (256, 256), color=(120, 150, 180))
    img.save(sample_path, "JPEG")
    print(f"Created test image at {sample_path}")

    detector = AIDetector()
    print("Analyzing test image with AIDetector...")
    results = detector.analyze(sample_path)
    print("Results:", results)

if __name__ == "__main__":
    main()
