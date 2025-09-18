Smart Farming Advisory System
================================

Prototype web app that provides basic, rule-based recommendations for farmers based on soil type and crop.

Stack
-----
- Frontend: React + Vite + TailwindCSS
- Backend: Node.js + Express
- Data: Static JSON rules in `backend/data/rules.json`

Quickstart (Windows PowerShell)
-------------------------------
1. Install Node.js 18+.
2. In the project root, run:
```powershell
npm install
```
This installs dependencies for both backend and frontend.

3. Start the backend and frontend:
```powershell
npm run dev
```
- Backend: http://localhost:5000
- Frontend: http://localhost:5173

If `npm run dev` doesn't open both, you can run them separately:
```powershell
npm run start:backend
npm run start:frontend
```

Customize rules
---------------
Edit `backend/data/rules.json`. Restart backend if running.

Environment
-----------
- Change API base for frontend via `.env` in `frontend/`:
```
VITE_API_BASE=http://localhost:5000
VITE_ML_API_BASE=http://localhost:8000
```

ML Disease Detection Service
---------------------------
- Location: `ml_backend/`
- Create and activate a Python 3.10+ venv, then:
```powershell
cd ml_backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```
- Test with curl:
```bash
curl -X POST "http://localhost:8000/api/detect" -F "image=@examples/leaf1.jpg"
```

Model notes:
- By default, a mock inference runs if `MODEL_PATH` is not provided.
- To use TensorFlow, install tensorflow and set `MODEL_PATH` to your `.h5` or SavedModel dir.
- To use TorchScript, install torch/torchvision and set `MODEL_PATH` to your `.pt` file.

This is a prototype for demonstration; consult local agronomic advisories for precise recommendations.

