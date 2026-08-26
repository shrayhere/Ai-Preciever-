import sys
import os
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from detectors.ai_detector import AIDetector
from detectors.forensics_detector import ForensicsDetector
from detectors.metadata_detector import MetadataDetector

def main():
    test_dir = os.path.dirname(__file__)
    sample_path = os.path.join(test_dir, "sample_test.jpg")
    
    ai_det = AIDetector()
    print("Testing AIDetector raw outputs:")
    res_ai = ai_det.analyze(sample_path)
    print(res_ai)

    meta_det = MetadataDetector()
    print("\nTesting MetadataDetector raw outputs:")
    res_meta = meta_det.analyze(sample_path)
    print(res_meta)

    forensic_det = ForensicsDetector()
    print("\nTesting ForensicsDetector raw outputs:")
    res_forensic = forensic_det.analyze(sample_path, output_heatmap_dir=test_dir)
    print(res_forensic)

if __name__ == "__main__":
    main()
