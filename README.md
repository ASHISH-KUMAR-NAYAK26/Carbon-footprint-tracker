Carbon Footprint Classification is a Machine Learning project that predicts carbon emission categories based on lifestyle and consumption patterns. It employs data preprocessing, feature engineering, exploratory analysis, and supervised learning techniques to identify key factors influencing environmental impact and generate actionable insights.

# Backend (FastAPI) for Carbon Footprint Tracker

This small FastAPI app exposes endpoints that the frontend can call:

- `GET /api/history` — returns rows from `Carbon Emission.csv` (if present).
- `GET /api/picks` — returns `picks.json` (or fallback items).
- `POST /api/estimate` — accepts input JSON and returns an estimate. If you place a trained model at `Backend/models/model.joblib` or `Backend/models/model.pkl`, the server will attempt to use it; otherwise it falls back to a heuristic calculation.

Quick start (Windows / PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Notes to integrate your trained model:
- Save a scikit-learn compatible predictor to `Backend/models/model.joblib` (or `model.pkl`).
- The backend expects `model.predict([[kmTraveled, electricityUsageKwh, transport_code, diet_code]])` to return a numeric CO2 estimate.

If you want the frontend to talk to this backend during development, run the backend and run the frontend dev server (Vite). By default the frontend calls relative `/api` routes — if you serve frontend with a proxy, configure Vite to proxy `/api` to `http://localhost:8000` in `vite.config.ts`.
