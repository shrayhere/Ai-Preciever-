import sys
import os
from transformers import pipeline

models_to_test = [
    "umm-maybe/AI-image-detector",
    "dima806/ai_vs_real_image_detection",
    "Smogy/SMOGY-Ai-images-detector"
]

def test_models():
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "uploads"))
    files = [f for f in os.listdir(upload_dir) if f.endswith(('.png', '.jpg', '.jpeg')) and not f.startswith('heatmap_')]
    
    print(f"Found {len(files)} files in uploads:")
    for f in files:
        print(" -", f)

    if not files:
        return

    chatgpt_files = [f for f in files if "chatgpt" in f.lower()]
    target_file = chatgpt_files[0] if chatgpt_files else files[0]
    sample_img = os.path.join(upload_dir, target_file)
    print(f"\nTesting on target image: {target_file}")

    for m in models_to_test:
        print(f"\n--- Model: {m} ---")
        try:
            pipe = pipeline("image-classification", model=m)
            out = pipe(sample_img)
            print("Output:", out)
        except Exception as e:
            print("Failed:", e)

if __name__ == "__main__":
    test_models()
