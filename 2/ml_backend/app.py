import os
import io
import uuid
import shutil
from typing import List, Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import numpy as np

# ----------------------------------------------------------------------------
# Configuration via environment variables
# ----------------------------------------------------------------------------
MODEL_PATH = os.getenv('MODEL_PATH', '')  # e.g., ./models/leaf_model.h5
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
MAX_UPLOAD_MB = float(os.getenv('MAX_UPLOAD_MB', '5'))
TEMP_DIR = os.getenv('TEMP_DIR', os.path.join(os.path.dirname(__file__), 'tmp'))

os.makedirs(TEMP_DIR, exist_ok=True)

# ----------------------------------------------------------------------------
# Disease labels and suggestions
# ----------------------------------------------------------------------------
DISEASE_LABELS: List[str] = [
    # Fungal
    'Leaf Spot',                # general
    'Rust',                     # orange/reddish pustules
    'Blight',                   # generic blight
    'Early Blight',             # tomato/potato
    'Late Blight',              # tomato/potato
    'Powdery Mildew',           # white powder
    'Downy Mildew',             # yellow top, gray underside
    'Anthracnose',              # dark sunken spots along veins
    'Gray Leaf Spot',           # maize
    # Bacterial
    'Bacterial Leaf Spot',
    'Bacterial Blight',
    'Canker',
    # Viral
    'Mosaic Virus',
    'Leaf Curl Virus',
    'Yellow Leaf Curl Virus',
    'Banana Streak/Stripe Viruses',
]

SUGGESTIONS: Dict[str, List[str]] = {
    'Leaf Spot': [
        'Remove infected leaves and dispose away from field.',
        'Avoid overhead irrigation; water at base.',
        'Apply a copper-based fungicide following label.',
    ],
    'Rust': [
        'Remove and destroy infected plant debris.',
        'Promote air flow between plants; reduce humidity.',
        'Use resistant cultivars where available.',
    ],
    'Blight': [
        'Rotate crops to avoid pathogen build-up.',
        'Apply recommended bactericide/fungicide per extension guidelines.',
    ],
    'Early Blight': [
        'Remove affected leaves; avoid overhead irrigation.',
        'Apply fungicide with chlorothalonil or copper as per label.',
        'Mulch soil to reduce spore splash.',
    ],
    'Late Blight': [
        'Immediately remove and destroy infected plants.',
        'Avoid leaf wetness; ensure good airflow.',
        'Follow extension guidance for appropriate fungicides.',
    ],
    'Powdery Mildew': [
        'Increase air circulation; avoid crowding plants.',
        'Apply sulfur or potassium bicarbonate-based products as labeled.',
        'Water at soil level; avoid wetting foliage.',
    ],
    'Downy Mildew': [
        'Improve air flow and reduce humidity.',
        'Use copper-based fungicides early; follow label.',
        'Remove infected leaves and debris.',
    ],
    'Anthracnose': [
        'Remove and destroy infected leaves and fruit.',
        'Avoid working in fields when foliage is wet.',
        'Apply recommended fungicides preventatively.',
    ],
    'Gray Leaf Spot': [
        'Rotate maize with non-host crops.',
        'Use resistant hybrids where available.',
        'Apply fungicide at early lesion appearance per guidance.',
    ],
    'Bacterial Leaf Spot': [
        'Use certified disease-free seed/seedlings.',
        'Copper bactericides can suppress; follow label.',
        'Avoid handling plants when wet; sanitize tools.',
    ],
    'Bacterial Blight': [
        'Remove infected plant material and improve drainage.',
        'Avoid overhead irrigation; sanitize tools and hands.',
        'Copper-based bactericides may help early; follow label.',
    ],
    'Canker': [
        'Prune 10–15 cm below symptoms during dry weather.',
        'Disinfect pruning tools between cuts.',
        'Apply copper-based products where recommended.',
    ],
    'Mosaic Virus': [
        'Control insect vectors (aphids/whiteflies) with IPM.',
        'Remove infected plants; avoid tobacco handling then touching plants.',
        'Use resistant varieties.',
    ],
    'Leaf Curl Virus': [
        'Manage whiteflies; use reflective mulches.',
        'Remove severely affected plants.',
        'Plant resistant/tolerant cultivars when possible.',
    ],
    'Yellow Leaf Curl Virus': [
        'Control whiteflies; use insect-proof nets for nurseries.',
        'Use resistant tomato varieties.',
        'Remove volunteer hosts and weeds.',
    ],
    'Banana Streak/Stripe Viruses': [
        'Use virus-free planting material.',
        'Control vector insects and remove infected leaves.',
        'Follow local extension advice for sanitation.',
    ],
    'low_confidence': [
        'Model confidence is low. Retake photo ensuring leaf is flat, well-lit, and fills most of frame.',
        'Try multiple images from different angles.',
    ],
}

# ----------------------------------------------------------------------------
# Model adapter with mock inference; pluggable backends
# ----------------------------------------------------------------------------

class ModelAdapter:
    def __init__(self, model_path: str | None):
        self.model_path = model_path or ''
        self.backend = None
        self.model = None
        self.input_size = (224, 224)
        self._load_model()

    def _load_model(self) -> None:
        if not self.model_path:
            # Mock mode: no real model provided
            self.backend = 'mock'
            return

        # Example TF loading (uncomment to enable):
        # try:
        #     import tensorflow as tf
        #     self.model = tf.keras.models.load_model(self.model_path)
        #     self.backend = 'tensorflow'
        #     return
        # except Exception as e:
        #     print('TensorFlow load failed, falling back to mock:', e)

        # Example Torch loading (uncomment to enable):
        # try:
        #     import torch
        #     self.model = torch.jit.load(self.model_path)
        #     self.model.eval()
        #     self.backend = 'torchscript'
        #     return
        # except Exception as e:
        #     print('Torch load failed, falling back to mock:', e)

        # Fallback to mock if no successful load
        self.backend = 'mock'

    def preprocess(self, pil_image: Image.Image) -> Any:
        image = pil_image.convert('RGB').resize(self.input_size)
        array = np.asarray(image).astype('float32') / 255.0
        # HWC -> for TF: (1, H, W, C); for Torch: (1, C, H, W)
        if self.backend == 'torchscript':
            array = np.transpose(array, (2, 0, 1))  # CHW
        array = np.expand_dims(array, 0)
        return array

    def predict_proba(self, input_tensor: Any) -> List[float]:
        if self.backend == 'tensorflow':
            import tensorflow as tf  # type: ignore
            preds = self.model.predict(input_tensor, verbose=0)
            probs = preds[0].tolist()
            return self._softmax(probs)
        if self.backend == 'torchscript':
            import torch  # type: ignore
            with torch.no_grad():
                tensor = torch.from_numpy(input_tensor).float()
                outputs = self.model(tensor)
                probs = torch.softmax(outputs, dim=1)[0].tolist()
                return probs
        # Mock backend: produce varied probabilities across all classes using simple color heuristics
        img = input_tensor[0]
        if img.ndim == 3 and img.shape[0] == 3:  # CHW (torch-style)
            r, g, b = img[0], img[1], img[2]
        else:  # HWC (tf-style)
            r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
        r_mean = float(np.mean(r))
        g_mean = float(np.mean(g))
        b_mean = float(np.mean(b))
        brightness = (r_mean + g_mean + b_mean) / 3.0

        n = len(DISEASE_LABELS)
        logits = np.ones((n,), dtype=np.float32) * 0.3

        idx = {name: i for i, name in enumerate(DISEASE_LABELS)}

        # Red dominance -> Rust, Leaf Spot, Anthracnose
        red_boost = max(r_mean - 0.4, 0.0)
        for name, factor in [('Rust', 3.0), ('Leaf Spot', 2.0), ('Anthracnose', 1.2)]:
            logits[idx[name]] += red_boost * factor

        # Green vs others -> mildews (Powdery/Downy)
        green_adv = max(g_mean - max(r_mean, b_mean), 0.0)
        for name in ['Powdery Mildew', 'Downy Mildew']:
            logits[idx[name]] += green_adv * 2.5

        # Darkness -> Blights
        dark = max(0.5 - brightness, 0.0)
        for name in ['Blight', 'Early Blight', 'Late Blight']:
            logits[idx[name]] += dark * 3.0

        # Contrast -> viral family
        contrast = float(np.std([r_mean, g_mean, b_mean]))
        for name in ['Mosaic Virus', 'Leaf Curl Virus', 'Yellow Leaf Curl Virus', 'Banana Streak/Stripe Viruses']:
            logits[idx[name]] += contrast * 1.2

        # Bacterial: red and green high relative to blue
        bacterial_signal = max(min(r_mean, g_mean) - b_mean, 0.0)
        for name in ['Bacterial Leaf Spot', 'Bacterial Blight', 'Canker']:
            logits[idx[name]] += bacterial_signal * 1.8

        # Gray Leaf Spot: moderate brightness with low blue component
        gls_signal = max((r_mean + g_mean) / 2 - b_mean - 0.05, 0.0)
        logits[idx['Gray Leaf Spot']] += gls_signal * 1.5

        # Normalize to softmax
        logits = logits - np.max(logits)
        exp = np.exp(logits)
        probs = (exp / np.sum(exp)).astype(np.float32)
        return probs.tolist()

    @staticmethod
    def _softmax(values: List[float]) -> List[float]:
        arr = np.array(values, dtype=np.float32)
        arr = arr - np.max(arr)
        exp = np.exp(arr)
        probs = exp / np.sum(exp)
        return probs.tolist()


model_adapter = ModelAdapter(MODEL_PATH)

app = FastAPI(title='Leaf Disease Detection API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def validate_image(upload: UploadFile) -> None:
    content_type = (upload.content_type or '').lower()
    if not content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail='Invalid image type.')
    filename = upload.filename or ''
    if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']):
        raise HTTPException(status_code=400, detail='Invalid image type.')


@app.post('/api/detect')
async def detect(image: UploadFile = File(...)):
    validate_image(image)

    size_limit = int(MAX_UPLOAD_MB * 1024 * 1024)
    # Read content with size guard
    contents = await image.read()
    if len(contents) > size_limit:
        raise HTTPException(status_code=413, detail='Image too large (max 5 MB).')

    # Save to temp file
    uid = str(uuid.uuid4())
    ext = os.path.splitext(image.filename or '')[1]
    safe_name = f'{uid}{ext}'
    tmp_path = os.path.join(TEMP_DIR, safe_name)
    with open(tmp_path, 'wb') as f:
        f.write(contents)

    try:
        pil = Image.open(io.BytesIO(contents))
        input_tensor = model_adapter.preprocess(pil)
        probs = model_adapter.predict_proba(input_tensor)
        # Normalize just in case
        probs_np = np.array(probs, dtype=np.float32)
        probs_np = probs_np / np.sum(probs_np)
        probs = probs_np.tolist()

        predictions = [
            { 'label': DISEASE_LABELS[i], 'probability': float(probs[i]) }
            for i in range(len(DISEASE_LABELS))
        ]
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        top = predictions[0]
        confidence = float(top['probability'])

        notes = ''
        sugg = dict(SUGGESTIONS)
        if confidence < 0.5:
            notes = 'If confidence < 0.5, show low_confidence suggestions'

        return JSONResponse({
            'predictions': predictions,
            'top_prediction': top,
            'suggestions': sugg,
            'confidence': confidence,
            'notes': notes,
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail='Inference failed') from e
    finally:
        # Clean up temp file
        try:
            os.remove(tmp_path)
        except Exception:
            pass


@app.get('/api/health')
async def health():
    return {'status': 'ok', 'backend': 'fastapi', 'model_backend': model_adapter.backend}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app:app', host='0.0.0.0', port=8000, reload=True)


