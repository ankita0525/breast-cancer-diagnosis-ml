import pickle
import os
import numpy as np
import pandas as pd

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")
PROC_DIR  = os.path.join(BASE_DIR, "..", "preprocessed")  # original preprocessed/

_model         = None
_scaler        = None
_feature_names = None


def _resolve_path(filename: str, directories: list[str]) -> str:
    """Try multiple directories for a file — returns first found path."""
    for d in directories:
        p = os.path.join(d, filename)
        if os.path.exists(p):
            return p
    return None


def load_ml_assets():
    """Load model, scaler, feature names. Uses cache after first load."""
    global _model, _scaler, _feature_names
    if _model is not None:
        return _model, _scaler, _feature_names

    search_dirs = [
        MODEL_DIR,
        PROC_DIR,
        os.path.join(BASE_DIR, "models"),
        os.path.join(BASE_DIR, "..", "preprocessed"),
        os.path.join(BASE_DIR, "..", "models"),
    ]

    model_path = _resolve_path("final_best_model.pkl", search_dirs)
    scaler_path = _resolve_path("scaler.pkl", search_dirs)
    features_path = _resolve_path("feature_names.pkl", search_dirs)

    if not model_path:
        raise FileNotFoundError("final_best_model.pkl not found. Run run_all.py first.")
    if not scaler_path:
        raise FileNotFoundError("scaler.pkl not found. Run run_all.py first.")
    if not features_path:
        raise FileNotFoundError("feature_names.pkl not found. Run run_all.py first.")

    with open(model_path, "rb") as f:
        _model = pickle.load(f)
    with open(scaler_path, "rb") as f:
        _scaler = pickle.load(f)
    with open(features_path, "rb") as f:
        _feature_names = pickle.load(f)

    return _model, _scaler, _feature_names


def predict(feature_values: dict) -> dict:
    """
    Run prediction on a dict of {feature_name: value}.
    Returns dict with prediction, confidence, risk_level, probability_malignant.
    """
    model, scaler, feature_names = load_ml_assets()

    # Build DataFrame in correct column order
    df = pd.DataFrame([feature_values])[feature_names]
    X_scaled = scaler.transform(df.values)

    pred_int  = model.predict(X_scaled)[0]
    probs     = model.predict_proba(X_scaled)[0] if hasattr(model, "predict_proba") else [0.5, 0.5]
    prob_mal  = float(probs[1])
    confidence = float(max(probs)) * 100

    prediction = "Malignant" if pred_int == 1 else "Benign"

    if prob_mal >= 0.75:
        risk_level = "High"
    elif prob_mal >= 0.50:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "prediction":            prediction,
        "confidence":            round(confidence, 2),
        "probability_malignant": round(prob_mal * 100, 2),
        "probability_benign":    round((1 - prob_mal) * 100, 2),
        "risk_level":            risk_level,
    }


def get_feature_names() -> list[str]:
    _, _, feature_names = load_ml_assets()
    return list(feature_names)
