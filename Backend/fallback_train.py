"""Fallback trainer that builds a very small pure-Python linear-style model
and saves it as `models/model.pkl`.

This avoids importing NumPy/scikit-learn so it can run even if binary
extensions are causing crashes. It builds four features to match the main
training script: [km, elec, transport_code, diet_code]. The model predicts
using simple per-feature linear fits (cov/var) combined with an intercept.
"""
import os
import csv
import pickle

BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "Carbon Emission.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PKL = os.path.join(MODEL_DIR, "model.pkl")


def read_csv_rows(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found at {path}")
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def build_features(records):
    X = []
    y = []

    # determine target column
    target_cols = ['CarbonEmission', 'Carbon Emission', 'Carbon_Emission']
    target_col = None
    if records:
        for c in target_cols:
            if c in records[0]:
                target_col = c
                break
    if target_col is None:
        raise ValueError('Target column not found in CSV')

    for row in records:
        # km
        km = 0.0
        for key in row:
            if 'Vehicle' in key and 'Distance' in key:
                try:
                    km = float(row.get(key) or 0)
                except:
                    km = 0.0
                break

        # elec: TV/Internet
        elec = 0.0
        for key in row:
            if 'How Long' in key and ('TV' in key or 'Internet' in key):
                try:
                    elec = float(row.get(key) or 0)
                except:
                    elec = 0.0
                break

        # transport code
        transport_val = str(row.get('Transport') or row.get('Vehicle Type') or '')
        transport_val = transport_val.lower()
        transport_code = 1 if any(x in transport_val for x in ['private', 'petrol', 'diesel', 'car']) else 0

        # diet code
        diet_val = str(row.get('Diet') or '')
        diet_val = diet_val.lower()
        if 'omnivore' in diet_val:
            diet_code = 2
        elif 'vegetarian' in diet_val:
            diet_code = 1
        else:
            diet_code = 0

        # target
        try:
            target = float(row.get(target_col) or 0)
        except:
            target = 0.0

        X.append([km, elec, transport_code, diet_code])
        y.append(target)

    return X, y


def mean(values):
    return sum(values) / len(values) if values else 0.0


def cov(x, y, mx=None, my=None):
    if mx is None:
        mx = mean(x)
    if my is None:
        my = mean(y)
    return sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / (len(x) - 1) if len(x) > 1 else 0.0


def var(x, mx=None):
    if mx is None:
        mx = mean(x)
    return sum((xi - mx) ** 2 for xi in x) / (len(x) - 1) if len(x) > 1 else 0.0


class SimpleLinearModel:
    def __init__(self, intercept=0.0, weights=None):
        self.intercept = intercept
        self.weights = weights or [0.0, 0.0, 0.0, 0.0]

    def predict(self, X):
        # Accept list of lists and return list-like
        out = []
        for row in X:
            s = self.intercept
            for w, xi in zip(self.weights, row):
                s += w * xi
            out.append(s)
        return out


def fit_simple_linear(X, y):
    # X: list of [f0,f1,f2,f3]
    # Compute per-feature slope = cov(feature, y) / var(feature)
    cols = list(zip(*X)) if X else [[], [], [], []]
    mx = [mean(col) for col in cols]
    my = mean(y)
    weights = []
    for i, col in enumerate(cols):
        v = var(col, mx[i])
        c = cov(col, y, mx[i], my)
        w = (c / v) if v != 0 else 0.0
        weights.append(w)
    intercept = my - sum(w * m for w, m in zip(weights, mx))
    return SimpleLinearModel(intercept=intercept, weights=weights)


def main():
    rows = read_csv_rows(CSV_PATH)
    X, y = build_features(rows)
    if not X:
        raise ValueError('No feature rows built from CSV')

    model = fit_simple_linear(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(MODEL_PKL, 'wb') as f:
        pickle.dump(model, f)
    print('Saved fallback pickle model to', MODEL_PKL)


if __name__ == '__main__':
    main()
