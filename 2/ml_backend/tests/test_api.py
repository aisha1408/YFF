import io
from PIL import Image
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def create_image_bytes():
    img = Image.new('RGB', (64, 64), color=(120, 200, 120))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue()


def test_upload_valid_image_returns_200_and_expected_schema():
    content = create_image_bytes()
    files = { 'image': ('leaf.png', content, 'image/png') }
    r = client.post('/api/detect', files=files)
    assert r.status_code == 200
    data = r.json()
    assert 'predictions' in data and isinstance(data['predictions'], list)
    assert 'top_prediction' in data
    assert 'confidence' in data
    assert 'suggestions' in data


def test_upload_non_image_returns_400():
    files = { 'image': ('not.txt', b'hello', 'text/plain') }
    r = client.post('/api/detect', files=files)
    assert r.status_code == 400
    assert 'Invalid image type' in r.text


def test_low_confidence_triggers_low_confidence_message(monkeypatch):
    # Force low confidence by monkeypatching predict_proba
    from app import model_adapter
    def low_conf(_):
        return [0.26, 0.25, 0.24, 0.25]
    monkeypatch.setattr(model_adapter, 'predict_proba', low_conf)

    content = create_image_bytes()
    files = { 'image': ('leaf.png', content, 'image/png') }
    r = client.post('/api/detect', files=files)
    assert r.status_code == 200
    data = r.json()
    assert data.get('notes', '').startswith('If confidence < 0.5')


