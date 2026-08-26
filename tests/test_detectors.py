import sys
import os
import unittest
import io
from PIL import Image, ImageDraw
import piexif

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from detectors.ai_detector import AIDetector
from detectors.forensics_detector import ForensicsDetector
from detectors.metadata_detector import MetadataDetector
from scoring.scorer import AuthenticityScorer
from database.db import init_db
from database.models import ScanRecord
from app import app

class TestDeepVerify(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.test_dir = os.path.dirname(__file__)
        cls.test_img_path = os.path.join(cls.test_dir, "test_unit.jpg")
        
        img = Image.new("RGB", (200, 200), color=(120, 140, 160))
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, 100, 100], fill=(200, 50, 50))

        exif_dict = {"0th": {piexif.ImageIFD.Make: b"Sony", piexif.ImageIFD.Model: b"A7III"}}
        exif_bytes = piexif.dump(exif_dict)
        img.save(cls.test_img_path, "JPEG", quality=90, exif=exif_bytes)

    def test_ai_detector(self):
        detector = AIDetector()
        res = detector.analyze(self.test_img_path)
        self.assertIn("ai_score", res)
        self.assertIn("label", res)
        self.assertEqual(res["status"], "success")

    def test_forensics_detector(self):
        detector = ForensicsDetector()
        res = detector.analyze(self.test_img_path, output_heatmap_dir=self.test_dir)
        self.assertIn("forensic_score", res)
        self.assertIn("ela_score", res)
        self.assertIn("fft_score", res)
        self.assertIn("heatmap_path", res)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, res["heatmap_path"])))

    def test_metadata_detector(self):
        detector = MetadataDetector()
        res = detector.analyze(self.test_img_path)
        self.assertTrue(res["has_exif"])
        self.assertEqual(res["camera_make"], "Sony")
        self.assertEqual(res["camera_model"], "A7III")

    def test_scorer(self):
        scorer = AuthenticityScorer()
        ai_res = {"ai_score": 0.1, "label": "Real"}
        forensic_res = {"forensic_score": 0.2, "ela_score": 0.1, "fft_score": 0.05, "noise_consistency_score": 0.2, "heatmap_path": "test.png"}
        metadata_res = {"metadata_score": 0.0, "flags": []}
        
        final_res = scorer.evaluate(ai_res, forensic_res, metadata_res)
        self.assertEqual(final_res["category"], "Likely Authentic")
        self.assertGreater(final_res["confidence_score"], 50.0)

    def test_database_and_routes(self):
        client = app.test_client()
        res = client.get("/")
        self.assertEqual(res.status_code, 200)

        res_history = client.get("/history")
        self.assertEqual(res_history.status_code, 200)

if __name__ == "__main__":
    unittest.main()
