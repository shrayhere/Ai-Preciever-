import sys
import os
import io
from PIL import Image

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

def main():
    client = app.test_client()

    print("Testing GET / ...")
    res = client.get("/")
    print(f"GET / Status: {res.status_code}")

    print("\nTesting POST /analyze with valid image...")
    img = Image.new("RGB", (200, 200), color=(100, 150, 200))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    data = {
        'image': (img_byte_arr, 'test_route.jpg', 'image/jpeg')
    }

    res_post = client.post("/analyze", data=data, content_type='multipart/form-data')
    print(f"POST /analyze Status: {res_post.status_code}")
    print("POST /analyze Data:", res_post.get_json())

    if res_post.status_code == 200 and res_post.get_json().get("success"):
        scan_id = res_post.get_json()["scan_id"]
        print(f"\nTesting GET /results/{scan_id} ...")
        res_results = client.get(f"/results/{scan_id}")
        print(f"GET /results/{scan_id} Status: {res_results.status_code}")

if __name__ == "__main__":
    main()
