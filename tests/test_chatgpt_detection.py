import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from detectors.ai_detector import AIDetector
from detectors.forensics_detector import ForensicsDetector
from detectors.metadata_detector import MetadataDetector
from scoring.scorer import AuthenticityScorer

def test_chatgpt_image():
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "uploads"))
    chatgpt_files = [f for f in os.listdir(upload_dir) if "chatgpt" in f.lower() and not f.startswith("heatmap_")]
    
    if not chatgpt_files:
        print("No ChatGPT images found in uploads!")
        return

    sample_img = os.path.join(upload_dir, chatgpt_files[0])
    print(f"Testing pipeline on ChatGPT image: {chatgpt_files[0]}")

    ai_det = AIDetector()
    forensic_det = ForensicsDetector()
    meta_det = MetadataDetector()
    scorer = AuthenticityScorer()

    ai_res = ai_det.analyze(sample_img)
    forensic_res = forensic_det.analyze(sample_img, output_heatmap_dir=upload_dir)
    meta_res = meta_det.analyze(sample_img)

    print("\n--- AI Detector Output ---")
    print(ai_res)

    print("\n--- Metadata Detector Output ---")
    print(meta_res)

    print("\n--- Forensic Detector Output ---")
    print(forensic_res)

    final_res = scorer.evaluate(ai_res, forensic_res, meta_res)
    print("\n--- FINAL EVALUATION RESULT ---")
    print(final_res)

    assert final_res["category"] == "Likely AI-Generated", f"Expected Likely AI-Generated, got {final_res['category']}"
    print("\nSUCCESS: ChatGPT image accurately detected as Likely AI-Generated!")

if __name__ == "__main__":
    test_chatgpt_image()
