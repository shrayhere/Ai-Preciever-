# DeepVerify (AI-Preciever) — AI Image Authenticity & Deepfake Detection Platform

DeepVerify is a web-based multi-signal image forensic analysis platform built with Python, Flask, PyTorch, and Hugging Face Vision Transformers. It evaluates uploaded images (JPG/JPEG/PNG) to determine whether they are **Likely Authentic**, **Possibly Manipulated**, or **Likely AI-Generated**, providing an explainable breakdown of forensic sub-scores, EXIF metadata, and generated Error Level Analysis (ELA) heatmaps.

---

## 🌟 Key Features

1. **AI Generation Detection (`detectors/ai_detector.py`)**
   - Employs Hugging Face `umm-maybe/AI-image-detector` Vision Transformer pipeline.
   - Accurately differentiates natural camera human photos (including web/WhatsApp compressed JPEGs) from AI-generated imagery (DALL-E 3, Midjourney, Stable Diffusion).

2. **Digital Forensics Analysis (`detectors/forensics_detector.py`)**
   - **Error Level Analysis (ELA):** Resaves images at fixed JPEG quality levels to compute pixel difference matrices, highlighting localized compression anomalies.
   - **2D FFT Noise Analysis:** Performs 2D Discrete Fourier Transform analysis to spot high-frequency periodic grid artifacts from generative upsampling.
   - **Block-Level Noise Consistency:** Evaluates variance residual across blocks to detect spliced or pasted regions.
   - **Visual Heatmap Generation:** Generates combined ELA and noise variance color map overlays for visual verification.

3. **Metadata Extraction (`detectors/metadata_detector.py`)**
   - Audits EXIF headers for camera hardware tags (Make, Model, Lens), photo editing software signatures (Photoshop, Canva, GIMP), and AI generator tags.

4. **Multi-Signal Cross-Validation (`scoring/scorer.py`)**
   - Cross-validates AI model confidence with physical ELA/FFT forensic evidence to prevent false-positive classifications on compressed photos.

5. **Recent Scan Audit Log Management (`database/models.py`, `templates/index.html`)**
   - Displays the last **7 recent scans** in an audit log dashboard with category badges and confidence metrics.
   - Features a **Clear Audit Log** button allowing users to delete audit log history and remove saved upload data from disk.

---

## 📁 Repository Structure

```
deepverify/
├── app.py                 # Flask application entry point
├── config.py              # Configuration settings & upload path
├── vercel.json            # Vercel serverless deployment setup
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── database/
│   ├── db.py              # SQLite connection & schema initialization
│   └── models.py          # ScanRecord model with get_recent and delete_all
├── detectors/
│   ├── base_detector.py   # Base detector class interface
│   ├── ai_detector.py     # AI generation Vision Transformer model
│   ├── forensics_detector.py # ELA, FFT, and noise variance analysis
│   └── metadata_detector.py  # EXIF metadata parser
├── routes/
│   └── main_routes.py     # Application routes (/analyze, /results, /clear_history)
├── scoring/
│   └── scorer.py          # Multi-signal authenticity evaluator
├── static/
│   ├── css/style.css      # Custom dark glassmorphism design system
│   ├── js/main.js         # File upload & clear audit log interactive JS
│   └── uploads/           # Generated visual heatmaps & user uploads
└── templates/
    ├── index.html         # Main upload dashboard & audit log table
    └── results.html       # Visual forensic analysis report view
```

---

## 🛠️ Local Installation & Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/shrayhere/Ai-Preciever-.git
   cd Ai-Preciever-
   ```

2. **Create & Activate Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch Application**
   ```bash
   python app.py
   ```
   Open `http://127.0.0.1:5000` in your web browser.

---

## 🧪 Running Tests

```bash
# Test individual detectors
python tests/test_detectors.py

# Test routes & standalone API logic
python tests/test_routes_standalone.py

# Test clear history functionality
python -c "from database.models import ScanRecord; print(ScanRecord.get_recent(7))"
```

---

## 🌐 Deployment

Designed for deployment on **Vercel** serverless Python runtime. Includes `vercel.json` configuration for single-command deployment:

```bash
vercel --prod
```
