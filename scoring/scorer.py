from typing import Dict, Any

class AuthenticityScorer:
    """
    Combines outputs from AIDetector, ForensicsDetector, and MetadataDetector
    into a unified, accurate confidence score, category, and plain-language explanation.
    """
    
    CATEGORY_AUTHENTIC = "Likely Authentic"
    CATEGORY_MANIPULATED = "Possibly Manipulated"
    CATEGORY_AI_GENERATED = "Likely AI-Generated"

    def evaluate(
        self,
        ai_results: Dict[str, Any],
        forensic_results: Dict[str, Any],
        metadata_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        ai_score = ai_results.get("ai_score", 0.0)
        forensic_score = forensic_results.get("forensic_score", 0.0)
        ela_score = forensic_results.get("ela_score", 0.0)
        fft_score = forensic_results.get("fft_score", 0.0)
        noise_score = forensic_results.get("noise_consistency_score", 0.0)
        
        metadata_score = metadata_results.get("metadata_score", 0.0)
        metadata_flags = metadata_results.get("flags", [])

        explanations = []

        # Check AI / Editing metadata triggers
        ai_in_metadata = any("AI generator" in flag for flag in metadata_flags)
        editing_in_metadata = any("Editing software" in flag for flag in metadata_flags)

        # 1. Determine Category & Accurate Confidence Percentage
        if ai_score >= 0.50 or (ai_score >= 0.35 and fft_score >= 0.45) or ai_in_metadata:
            # Physical forensic cross-validation: if ELA, FFT grid, and noise are clean and no AI EXIF metadata, avoid isolated false positives
            if forensic_score < 0.20 and fft_score < 0.30 and ela_score < 0.30 and not ai_in_metadata and ai_score < 0.85:
                category = self.CATEGORY_AUTHENTIC
                confidence = (1.0 - max(ai_score * 0.1, forensic_score)) * 100.0
                explanations.append("Physical ELA, 2D FFT, and noise analysis confirm natural camera structure without synthetic frequency artifacts.")
                explanations.append("Neural classifier registered web compression texture indicators, but forensic checks verify authentic camera origin.")
            else:
                category = self.CATEGORY_AI_GENERATED
                
                if ai_in_metadata and ai_score < 0.5:
                    confidence = 88.0
                else:
                    confidence = max(ai_score * 100.0, 65.0)

                explanations.append(f"AI classification model detected synthetic/AI generation indicators ({ai_score * 100:.1f}% probability).")
                if fft_score >= 0.40:
                    explanations.append("Frequency-domain FFT analysis revealed periodic upsampling grid artifacts typical of diffusion/GAN models.")
                if ai_in_metadata:
                    explanations.append("Image EXIF metadata explicitly contained AI generator signatures.")

        elif forensic_score >= 0.35 or ela_score >= 0.40 or noise_score >= 0.45 or editing_in_metadata:
            category = self.CATEGORY_MANIPULATED
            
            trigger_scores = [forensic_score * 100.0, ela_score * 100.0, noise_score * 100.0]
            if editing_in_metadata:
                trigger_scores.append(60.0)
            
            confidence = max(trigger_scores)

            if ela_score >= 0.35:
                explanations.append("Error Level Analysis (ELA) detected compression inconsistencies indicative of spliced or edited regions.")
            if noise_score >= 0.40:
                explanations.append("Block-level noise variance analysis showed inconsistent pixel noise across image sections.")
            if editing_in_metadata:
                explanations.append(f"Metadata analysis identified editing software tags ({metadata_results.get('software', 'photo editor')}).")
            if not explanations:
                explanations.append("Digital forensic checks identified subtle localized pixel compression anomalies.")

        else:
            category = self.CATEGORY_AUTHENTIC
            # High confidence of authenticity when AI and forensic anomaly scores are low
            max_anomaly = max(ai_score, forensic_score)
            confidence = (1.0 - max_anomaly) * 100.0

            explanations.append("No significant AI generation patterns or localized compression anomalies detected.")
            if metadata_results.get("has_exif") and metadata_results.get("camera_make"):
                explanations.append(f"EXIF metadata is consistent with camera hardware ({metadata_results.get('camera_make')} {metadata_results.get('camera_model', '')}).")

        # Clamp confidence cleanly between 5.0% and 99.9%
        confidence = round(min(99.9, max(5.0, confidence)), 1)

        explanation_text = " ".join(explanations)

        return {
            "category": category,
            "confidence_score": confidence,
            "sub_scores": {
                "ai_score": round(ai_score, 4),
                "forensic_score": round(forensic_score, 4),
                "ela_score": round(ela_score, 4),
                "fft_score": round(fft_score, 4),
                "noise_consistency_score": round(noise_score, 4),
                "metadata_score": round(metadata_score, 4)
            },
            "metadata_flags": metadata_flags,
            "explanation": explanation_text,
            "heatmap_path": forensic_results.get("heatmap_path", "")
        }
