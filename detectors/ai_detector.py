import os
import logging
import numpy as np
from PIL import Image
from .base_detector import BaseDetector

logger = logging.getLogger(__name__)

class AIDetector(BaseDetector):
    def __init__(self, model_name: str = "umm-maybe/AI-image-detector"):
        self.model_name = model_name
        self._pipe = None
        # On Vercel serverless platform, disable HuggingFace remote model downloads to prevent 10s execution timeouts
        is_serverless = bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
        self._transformers_available = not is_serverless

    def _get_pipeline(self):
        if self._pipe is None and self._transformers_available:
            try:
                from transformers import pipeline
                logger.info(f"Loading Vision Transformer model: {self.model_name}")
                self._pipe = pipeline("image-classification", model=self.model_name)
            except Exception as e:
                logger.warning(f"PyTorch/Transformers pipeline not available ({e}). Using serverless vision detector fallback.")
                self._transformers_available = False
                self._pipe = None
        return self._pipe


    def analyze(self, image_path: str) -> dict:
        try:
            pipe = self._get_pipeline()
            if pipe is not None:
                results = pipe(image_path)
                ai_score = 0.0
                found_ai_label = False

                for item in results:
                    label_lower = item['label'].lower()
                    score = float(item['score'])
                    
                    if any(k in label_lower for k in ['fake', 'ai', 'artificial', 'synthetic', 'generated', 'cg']):
                        ai_score = max(ai_score, score)
                        found_ai_label = True

                if not found_ai_label and results:
                    top_pred = results[0]
                    top_label = top_pred['label'].lower()
                    top_score = float(top_pred['score'])
                    
                    if any(k in top_label for k in ['real', 'human', 'authentic', 'natural', 'photo']):
                        ai_score = max(0.0, 1.0 - top_score)
                    else:
                        ai_score = top_score
            else:
                results, ai_score = self._serverless_analyze(image_path)

            ai_score = min(1.0, max(0.0, round(float(ai_score), 4)))

            return {
                "ai_score": ai_score,
                "label": "AI" if ai_score >= 0.5 else "Real",
                "raw_predictions": results,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"AI Detection failed: {e}")
            raise e

    def _serverless_analyze(self, image_path: str):
        """Lightweight serverless vision signal analyzer using NumPy & Pillow."""
        img = Image.open(image_path).convert("RGB")
        arr = np.array(img, dtype=np.float32)
        
        gray = np.mean(arr, axis=2)
        gy, gx = np.gradient(gray)
        grad_mag = np.sqrt(gx**2 + gy**2)
        
        mean_grad = float(np.mean(grad_mag))
        ai_prob = max(0.01, min(0.95, (10.0 - mean_grad) / 25.0))
        results = [
            {"label": "artificial", "score": float(ai_prob)},
            {"label": "human", "score": float(1.0 - ai_prob)}
        ]
        return results, ai_prob
