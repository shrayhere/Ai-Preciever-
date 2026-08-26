import logging
from transformers import pipeline
from .base_detector import BaseDetector

logger = logging.getLogger(__name__)

class AIDetector(BaseDetector):
    def __init__(self, model_name: str = "umm-maybe/AI-image-detector"):
        self.model_name = model_name
        self._pipe = None

    def _get_pipeline(self):
        if self._pipe is None:
            logger.info(f"Loading Vision Transformer model: {self.model_name}")
            self._pipe = pipeline("image-classification", model=self.model_name)
        return self._pipe

    def analyze(self, image_path: str) -> dict:
        try:
            pipe = self._get_pipeline()
            results = pipe(image_path)
            
            ai_score = 0.0
            found_ai_label = False

            for item in results:
                label_lower = item['label'].lower()
                score = float(item['score'])
                
                # 'fake', 'ai', 'artificial', 'synthetic', 'generated', 'cg'
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
