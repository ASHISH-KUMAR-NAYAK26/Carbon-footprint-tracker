from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import os
import json

app = FastAPI(title="Carbon Footprint Backend")

# Allow CORS for dev and local usage. Adjust origins in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "Carbon Emission.csv")
PICKS_PATH = os.path.join(BASE_DIR, "picks.json")
MODEL_DIR = os.path.join(BASE_DIR, "models")


class EstimateInputs(BaseModel):
    kmTraveled: float = 0
    transportType: str = "car"
    electricityUsageKwh: float = 0
    dietType: str = "omnivore"
    goodsPurchased: Optional[str] = ""


def load_csv():
    if not os.path.exists(CSV_PATH):
        return None
    try:
        df = pd.read_csv(CSV_PATH)
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {e}")


@app.get("/api/history")
def history():
    df = load_csv()
    if df is None:
        return []

    # Try to provide monthly aggregates if date/month column exists
    # Otherwise return top N rows
    if "month" in df.columns:
        data = df.to_dict(orient="records")
        return data
    else:
        return df.head(100).to_dict(orient="records")


@app.get("/api/picks")
def picks():
    if os.path.exists(PICKS_PATH):
        with open(PICKS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    # Fallback picks
    return [
        {"id": "led", "title": "Switch to LED", "description": "Replace bulbs with LEDs.", "co2SavedKg": 25, "category": "energy", "imageUrl": "https://picsum.photos/200/200?random=10"},
        {"id": "meatless", "title": "Meatless Mondays", "description": "Skip meat once a week.", "co2SavedKg": 18, "category": "food", "imageUrl": "https://picsum.photos/200/200?random=11"}
    ]


@app.post("/api/estimate")
def estimate(inputs: EstimateInputs):
    # If user placed a trained model in Backend/models (joblib/pickle), try to use it.
    model_path_joblib = os.path.join(MODEL_DIR, "model.joblib")
    model_path_pkl = os.path.join(MODEL_DIR, "model.pkl")

    # Local heuristic fallback
    transportFactor = 0.2 if inputs.transportType == "car" else 0.05
    electFactor = 0.5
    foodBase = 5 if inputs.dietType == "vegan" else 8 if inputs.dietType == "vegetarian" else 15

    t = inputs.kmTraveled * transportFactor
    e = inputs.electricityUsageKwh * electFactor
    f = foodBase * 30
    g = 50

    result = {
        "totalKgCO2": round(t + e + f + g, 1),
        "breakdown": {"transport": round(t, 1), "electricity": round(e, 1), "food": round(f, 1), "goods": g},
        "aiAnalysis": "Heuristic estimate from backend. Place a trained model in Backend/models/model.joblib to use your model.",
        "confidenceScore": 0.6
    }

    # Attempt to load model if present
    try:
        if os.path.exists(model_path_joblib):
            import joblib
            model = joblib.load(model_path_joblib)
            # Expect model.predict to accept a 2D array-like: [kmTraveled, electricityUsageKwh, transportType_code, diet_code]
            transport_code = 1 if inputs.transportType == 'car' else 0
            diet_code = 2 if inputs.dietType == 'omnivore' else 1 if inputs.dietType == 'vegetarian' else 0
            X = [[inputs.kmTraveled, inputs.electricityUsageKwh, transport_code, diet_code]]
            pred = model.predict(X)
            result['totalKgCO2'] = float(pred[0])
            result['aiAnalysis'] = 'Predicted by user model (model.joblib).'
            result['confidenceScore'] = 0.85
            return result
        elif os.path.exists(model_path_pkl):
            import pickle
            with open(model_path_pkl, 'rb') as f:
                model = pickle.load(f)
            transport_code = 1 if inputs.transportType == 'car' else 0
            diet_code = 2 if inputs.dietType == 'omnivore' else 1 if inputs.dietType == 'vegetarian' else 0
            X = [[inputs.kmTraveled, inputs.electricityUsageKwh, transport_code, diet_code]]
            pred = model.predict(X)
            result['totalKgCO2'] = float(pred[0])
            result['aiAnalysis'] = 'Predicted by user model (model.pkl).'
            result['confidenceScore'] = 0.85
            return result
    except Exception as e:
        # If model fails, return heuristic with a note
        result['aiAnalysis'] += f" Model load/predict failed: {e}"

    return result


@app.get("/api/predict_all")
def predict_all():
    """Run the user's model (if present) over the CSV and return predictions.

    Returns an array of objects: { index, predicted: float, actual: optional }
    """
    model_path_joblib = os.path.join(MODEL_DIR, "model.joblib")
    model_path_pkl = os.path.join(MODEL_DIR, "model.pkl")

    if not os.path.exists(model_path_joblib) and not os.path.exists(model_path_pkl):
        return {"error": "No model found in Backend/models. Place model.joblib or model.pkl to enable batch predictions."}

    df = load_csv()
    if df is None:
        raise HTTPException(status_code=404, detail="CSV not found")

    # Build feature matrix for each row. This uses a simple mapping; adjust if your model expects different features.
    records = df.to_dict(orient="records")
    X = []
    for row in records:
        # Extract numeric vehicle monthly km
        km = None
        for key in ["Vehicle Monthly Distance Km", "Vehicle Monthly Distance Km ", "vehicle_monthly_distance_km"]:
            if key in row:
                try:
                    km = float(row.get(key) if row.get(key) != '' else 0)
                except:
                    km = 0.0
                break
        if km is None:
            km = 0.0

        # Proxy electricity with 'How Long TV PC Daily Hour' or 'How Long Internet Daily Hour'
        elec = 0.0
        for key in ["How Long TV PC Daily Hour", "How Long Internet Daily Hour", "How Long TV PC Daily Hour "]:
            if key in row:
                try:
                    elec = float(row.get(key) if row.get(key) != '' else 0)
                except:
                    elec = 0.0
                break

        transport = str(row.get('Transport') or row.get('Vehicle Type') or '').lower()
        transport_code = 1 if 'private' in transport or 'car' in transport or 'petrol' in transport or 'diesel' in transport else 0

        diet = str(row.get('Diet') or '').lower()
        diet_code = 2 if 'omnivore' in diet else 1 if 'vegetarian' in diet else 0

        X.append([km, elec, transport_code, diet_code])

    # Load model and predict
    preds = []
    try:
        if os.path.exists(model_path_joblib):
            import joblib
            model = joblib.load(model_path_joblib)
        else:
            import pickle
            with open(model_path_pkl, 'rb') as f:
                model = pickle.load(f)

        raw_preds = model.predict(X)

        for i, p in enumerate(raw_preds):
            actual = None
            for col in ['CarbonEmission', 'CarbonEmission ', 'Carbon Emission', 'Carbon_Emission']:
                if col in records[i]:
                    try:
                        actual = float(records[i].get(col))
                    except:
                        actual = None
                    break
            preds.append({"index": i, "predicted": float(p), "actual": actual})

        return {"count": len(preds), "predictions": preds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model predict failed: {e}")
