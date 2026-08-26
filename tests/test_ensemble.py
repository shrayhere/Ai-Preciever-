import sys
import os
from transformers import pipeline

def main():
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "uploads"))
    
    chatgpt_img = os.path.join(upload_dir, "02df8ba1229c418e88698003934e0fda_ChatGPT_Image_Aug_25_2026_11_36_34_PM.png")
    real_webcam = os.path.join(upload_dir, "514f680474684dde8301a7a2600af664_WIN_20260810_15_11_59_Pro.jpg")

    pipe1 = pipeline("image-classification", model="dima806/ai_vs_real_image_detection")
    pipe2 = pipeline("image-classification", model="umm-maybe/AI-image-detector")

    for name, img_path in [("ChatGPT DALL-E 3 Image", chatgpt_img), ("Real Webcam Photo", real_webcam)]:
        print(f"\n================ {name} ================")
        out1 = pipe1(img_path)
        out2 = pipe2(img_path)
        
        # out1: FAKE vs REAL
        score_fake_1 = next(item['score'] for item in out1 if item['label'].upper() == 'FAKE')
        # out2: artificial vs human
        score_fake_2 = next(item['score'] for item in out2 if item['label'].lower() in ['artificial', 'ai', 'fake', 'synthetic'])

        avg_score = (score_fake_1 + score_fake_2) / 2.0
        print(f"Model 1 (dima806) AI Score: {score_fake_1:.4f}")
        print(f"Model 2 (umm-maybe) AI Score: {score_fake_2:.4f}")
        print(f"Ensemble Average AI Score: {avg_score:.4f}")

if __name__ == "__main__":
    main()
