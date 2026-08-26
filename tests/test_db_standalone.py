import sys
import os

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db import init_db
from database.models import ScanRecord

def main():
    print("Initializing DB...")
    init_db()

    print("Inserting sample scan record...")
    scan_id = ScanRecord.create(
        filename="test_image.jpg",
        ai_score=0.12,
        forensic_score=0.45,
        metadata_flags=["Editing software signature detected: photoshop"],
        final_score=68.5,
        category="Possibly Manipulated",
        explanation="Detected localized compression anomaly.",
        heatmap_path="heatmap_test_image.png"
    )
    print(f"Inserted record with scan_id: {scan_id}")

    print("Retrieving record by ID...")
    rec = ScanRecord.get_by_id(scan_id)
    print("Retrieved record:", rec)

    print("Retrieving recent records...")
    recent = ScanRecord.get_recent(5)
    print(f"Total recent records retrieved: {len(recent)}")

if __name__ == "__main__":
    main()
