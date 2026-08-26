import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from detectors.ai_detector import AIDetector
from detectors.forensics_detector import ForensicsDetector
from detectors.metadata_detector import MetadataDetector
from scoring.scorer import AuthenticityScorer

def main():
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "uploads"))
    real_files = [f for f in os.listdir(upload_dir) if f.startswith("514f680474684dde8301a7a2600af664_WIN_") or f.startswith("b0cede00a1b8461d84a52a8527bbc1c4_WIN_")]
    
    ai_det = AIDetector()
    forensic_det = ForensicsDetector()
    meta_det = MetadataDetector()
    scorer = AuthenticityScorer()

    for rf in real_files:
        p = os.path.join(upload_dir, rf)
        print(f"\nAnalyzing real webcam photo: {rf}")
        ai_res = ai_det.analyze(p)
        forensic_res = forensic_det.analyze(p, output_heatmap_dir=upload_dir)
        meta_res = meta_det.analyze(p)

        print("AI Res:", ai_res)
        print("Meta Res:", meta_res)
        print("Forensic Res:", forensic_res)

        final_res = scorer.evaluate(ai_res, forensic_res, meta_res)
        print("Final Evaluation:", final_res)

if __name__ == "__main__":
    main()
