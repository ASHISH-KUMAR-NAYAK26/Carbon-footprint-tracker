"""Train a simple regression model from `Carbon Emission.csv` and save as `models/model.joblib`.

This script uses a small feature set consistent with the backend prediction adapter:
- km: vehicle monthly distance (if present)
- elec: proxy for electricity use (TV/Internet hours)
- transport_code: 1 for private/car-like, 0 otherwise
- diet_code: 2 omnivore, 1 vegetarian, 0 vegan/other

It trains a RandomForestRegressor and saves the model to `models/model.joblib`.
"""
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "Carbon Emission.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "model.joblib")
MODEL_PKL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")


def load_data():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV not found at {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    return df


def build_features(df: pd.DataFrame):
    records = df.copy()

    # km feature: try common column names
    km_cols = [c for c in records.columns if 'Vehicle' in c and 'Distance' in c]
    if km_cols:
        km_col = km_cols[0]
        records['km'] = pd.to_numeric(records[km_col], errors='coerce').fillna(0)
    else:
        records['km'] = 0.0

    # elec proxy: TV/Internet hours
    elec_cols = [c for c in records.columns if 'How Long' in c and ('TV' in c or 'Internet' in c)]
    if elec_cols:
        elec_col = elec_cols[0]
        records['elec'] = pd.to_numeric(records[elec_col], errors='coerce').fillna(0)
    else:
        records['elec'] = 0.0

    # transport_code
    def tcode(val):
        if not isinstance(val, str):
            return 0
        v = val.lower()
        if any(x in v for x in ['private', 'petrol', 'diesel', 'car']):
            return 1
        return 0

    # prefer explicit Transport column
    if 'Transport' in records.columns:
        records['transport_code'] = records['Transport'].astype(str).map(tcode).fillna(0).astype(int)
    else:
        records['transport_code'] = 0

    # diet_code
    def dcode(val):
        if not isinstance(val, str):
            return 2
        v = val.lower()
        if 'omnivore' in v:
            return 2
        if 'vegetarian' in v:
            return 1
        return 0

    if 'Diet' in records.columns:
        records['diet_code'] = records['Diet'].astype(str).map(dcode).fillna(2).astype(int)
    else:
        records['diet_code'] = 2

    # target column names to try
    target_cols = ['CarbonEmission', 'Carbon Emission', 'Carbon_Emission']
    target = None
    for c in target_cols:
        if c in records.columns:
            target = c
            break
    if target is None:
        raise ValueError('Target column (CarbonEmission) not found in CSV')

    X = records[['km', 'elec', 'transport_code', 'diet_code']].values
    y = pd.to_numeric(records[target], errors='coerce').fillna(0).values
    return X, y


def train_and_save():
    print('Loading CSV...')
    df = load_data()
    print('Building features...')
    X, y = build_features(df)

    print('Train/test split...')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    print('Training RandomForestRegressor...')
    model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    print('Evaluating...')
    preds = model.predict(X_test)
    print('MAE:', mean_absolute_error(y_test, preds))
    print('R2:', r2_score(y_test, preds))

    print('Saving model to', MODEL_PATH)
    joblib.dump(model, MODEL_PATH)
    # Also save a pickle (.pkl) file for compatibility with other loaders
    try:
        import pickle
        with open(MODEL_PKL_PATH, 'wb') as f:
            pickle.dump(model, f)
        print('Saved pickle model to', MODEL_PKL_PATH)
    except Exception as e:
        print('Failed to save pickle model:', e)
    print('Saved successfully.')


if __name__ == '__main__':
    os.makedirs(os.path.join(BASE_DIR, 'models'), exist_ok=True)
    train_and_save()
