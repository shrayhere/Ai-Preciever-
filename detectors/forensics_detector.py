import os
import io
import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageFilter
from .base_detector import BaseDetector

def apply_jet_colormap(gray_arr: np.ndarray) -> np.ndarray:
    """Applies JET colormap to 2D uint8 numpy array, returning RGB uint8 array."""
    x = np.clip(gray_arr.astype(float) / 255.0, 0.0, 1.0)
    r = np.clip(1.5 - np.abs(4.0 * x - 3.0), 0.0, 1.0)
    g = np.clip(1.5 - np.abs(4.0 * x - 2.0), 0.0, 1.0)
    b = np.clip(1.5 - np.abs(4.0 * x - 1.0), 0.0, 1.0)
    rgb = np.stack([r, g, b], axis=-1) * 255.0
    return rgb.astype(np.uint8)

class ForensicsDetector(BaseDetector):
    def __init__(self, ela_quality: int = 90, scale: int = 15):
        self.ela_quality = ela_quality
        self.scale = scale

    def analyze(self, image_path: str, output_heatmap_dir: str = None) -> dict:
        """
        Performs Error Level Analysis (ELA), FFT noise analysis, and Block-level noise consistency check.
        Generates and saves visual ELA/Noise heatmap.
        """
        # 1. Error Level Analysis (ELA)
        ela_diff_arr, ela_score = self._compute_ela(image_path)

        # 2. FFT Noise Analysis
        fft_score, fft_magnitude = self._compute_fft_analysis(image_path)

        # 3. Block-Level Noise Consistency
        noise_score, block_variance_map = self._compute_block_noise_consistency(image_path)

        # 4. Generate Combined Visual Heatmap
        heatmap_path = self._generate_heatmap(
            image_path=image_path,
            ela_diff_arr=ela_diff_arr,
            block_variance_map=block_variance_map,
            output_dir=output_heatmap_dir
        )

        # 5. Composite Forensic Score (weighted combination 0.0 - 1.0)
        composite_score = min(1.0, round((ela_score * 0.45 + fft_score * 0.25 + noise_score * 0.30), 4))

        return {
            "forensic_score": composite_score,
            "ela_score": round(float(ela_score), 4),
            "fft_score": round(float(fft_score), 4),
            "noise_consistency_score": round(float(noise_score), 4),
            "heatmap_path": heatmap_path,
            "details": {
                "ela_compression_anomaly": ela_score > 0.35,
                "fft_periodic_artifact": fft_score > 0.45,
                "inconsistent_block_noise": noise_score > 0.40
            },
            "status": "success"
        }

    def _compute_ela(self, image_path: str):
        """Re-saves image at JPEG quality and calculates difference."""
        original = Image.open(image_path).convert("RGB")
        
        # Save to memory at defined JPEG quality
        buf = io.BytesIO()
        original.save(buf, "JPEG", quality=self.ela_quality)
        buf.seek(0)
        resaved = Image.open(buf).convert("RGB")

        # Compute pixel difference
        ela_diff = ImageChops.difference(original, resaved)

        # Enhance difference scale
        extrema = ela_diff.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0:
            max_diff = 1
        scale = 255.0 / max_diff

        ela_enhanced = ImageEnhance.Brightness(ela_diff).enhance(scale)
        diff_arr = np.array(ela_enhanced)

        # Calculate numeric anomaly score based on mean and std dev of differences
        gray_diff = np.mean(diff_arr, axis=2)
        mean_val = np.mean(gray_diff)
        std_val = np.std(gray_diff)
        
        # Standardized ELA metric
        ela_score = min(1.0, max(0.0, (mean_val * 0.005 + (std_val / 256.0) * 0.3)))
        return diff_arr, float(ela_score)

    def _compute_fft_analysis(self, image_path: str):
        """2D Fourier Transform to analyze frequency domain noise patterns."""
        pil_img = Image.open(image_path).convert("L")
        img = np.array(pil_img, dtype=float)

        # 2D FFT
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        magnitude = 20 * np.log(np.abs(fshift) + 1e-8)

        # High frequency analysis (outer regions of magnitude spectrum)
        h, w = magnitude.shape
        cy, cx = h // 2, w // 2
        
        # Mask out center (low frequencies)
        radius = min(h, w) // 8
        y, x = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((x - cx)**2 + (y - cy)**2)
        high_freq_mask = dist_from_center > radius

        high_freq_vals = magnitude[high_freq_mask]
        
        std_hf = np.std(high_freq_vals)
        p95_hf = np.percentile(high_freq_vals, 95)
        median_hf = np.median(high_freq_vals)
        
        peak_ratio = (p95_hf - median_hf) / (std_hf + 1e-5)
        fft_score = min(1.0, max(0.0, (peak_ratio - 2.0) / 4.0))

        return float(fft_score), magnitude

    def _compute_block_noise_consistency(self, image_path: str, block_size: int = 32):
        """Splits noise residual into grid blocks and computes local noise variance consistency."""
        pil_img = Image.open(image_path).convert("L")
        img_arr = np.array(pil_img, dtype=np.float32)

        h, w = img_arr.shape
        
        # Extract noise residual by subtracting Gaussian blurred background
        blurred_pil = pil_img.filter(ImageFilter.GaussianBlur(radius=1.0))
        blurred_arr = np.array(blurred_pil, dtype=np.float32)
        noise_residual = np.abs(img_arr - blurred_arr)

        blocks_y = h // block_size
        blocks_x = w // block_size

        if blocks_y == 0 or blocks_x == 0:
            return 0.0, np.zeros((h, w), dtype=np.float32)

        variance_grid = np.zeros((blocks_y, blocks_x), dtype=np.float32)

        for i in range(blocks_y):
            for j in range(blocks_x):
                block = noise_residual[i*block_size:(i+1)*block_size, j*block_size:(j+1)*block_size]
                variance_grid[i, j] = np.var(block)

        mean_var = np.mean(variance_grid)
        std_var = np.std(variance_grid)

        # Coefficient of variation across noise residual blocks
        cov = std_var / (mean_var + 1e-5)
        # Normal portrait photos naturally have COV ~1.5 - 2.5 between background & subject textures
        noise_score = min(1.0, max(0.0, (cov - 2.5) / 3.0))

        # Resize variance grid to full image size
        grid_pil = Image.fromarray(variance_grid)
        resized_grid = grid_pil.resize((w, h), Image.NEAREST)
        block_variance_map = np.array(resized_grid, dtype=np.float32)

        return float(noise_score), block_variance_map

    def _generate_heatmap(self, image_path: str, ela_diff_arr: np.ndarray, block_variance_map: np.ndarray, output_dir: str = None) -> str:
        """Generates and saves visual forensic color heatmap image."""
        if ela_diff_arr.ndim == 3:
            gray_ela = np.mean(ela_diff_arr, axis=2).astype(np.float32)
        else:
            gray_ela = ela_diff_arr.astype(np.float32)

        bv_min, bv_max = block_variance_map.min(), block_variance_map.max()
        if bv_max > bv_min:
            norm_var = ((block_variance_map - bv_min) / (bv_max - bv_min)) * 255.0
        else:
            norm_var = np.zeros_like(block_variance_map, dtype=np.float32)

        combined_map = (gray_ela * 0.6 + norm_var * 0.4)
        combined_norm = np.clip(combined_map, 0, 255).astype(np.uint8)

        color_heatmap_rgb = apply_jet_colormap(combined_norm)

        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(image_path), "..", "static", "uploads")

        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception:
            pass

        base_name = os.path.splitext(os.path.basename(image_path))[0]
        heatmap_filename = f"heatmap_{base_name}.png"
        save_path = os.path.join(output_dir, heatmap_filename)

        Image.fromarray(color_heatmap_rgb).save(save_path)
        return heatmap_filename

