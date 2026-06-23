"""
CitizenVoice AI - Inference Utilities

Loads the three trained pipelines (department, sentiment, priority) and
exposes a single `analyze_transcript()` function used by the Upload and
AI Analysis pages.
"""

import os
import joblib
import numpy as np

from utils.preprocessing import preprocess_for_vectorizer, extract_keywords, extract_locations

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
MODELS_DIR = os.path.join(BASE_DIR, "models")

_models_cache = {}


def _load(name, filename):
    if name not in _models_cache:
        path = os.path.join(MODELS_DIR, filename)
        _models_cache[name] = joblib.load(path)
    return _models_cache[name]


def load_models():
    """Eagerly loads and caches all three models. Call once at app startup."""
    return {
        "department": _load("department", "classifier.pkl"),
        "sentiment": _load("sentiment", "sentiment.pkl"),
        "priority": _load("priority", "priority.pkl"),
    }


def _predict_with_confidence(pipeline, clean_text):
    label = pipeline.predict([clean_text])[0]
    confidence = None
    if hasattr(pipeline, "predict_proba"):
        try:
            proba = pipeline.predict_proba([clean_text])[0]
            confidence = float(np.max(proba))
        except Exception:
            confidence = None
    return label, confidence


def analyze_transcript(transcript: str) -> dict:
    """
    Runs the full AI pipeline on a single transcript and returns a dict with:
    department, department_confidence, sentiment, sentiment_confidence,
    priority, priority_confidence, keywords, locations, clean_text
    """
    models = load_models()
    clean_text = preprocess_for_vectorizer(transcript)

    if not clean_text:
        return {
            "department": "Unclassified",
            "department_confidence": 0.0,
            "sentiment": "Neutral",
            "sentiment_confidence": 0.0,
            "priority": "Low",
            "priority_confidence": 0.0,
            "keywords": [],
            "locations": [],
            "clean_text": "",
        }

    dept, dept_conf = _predict_with_confidence(models["department"], clean_text)
    sentiment, sent_conf = _predict_with_confidence(models["sentiment"], clean_text)
    priority, prio_conf = _predict_with_confidence(models["priority"], clean_text)

    keywords = extract_keywords(transcript, top_n=8)
    locations = extract_locations(transcript)

    return {
        "department": dept,
        "department_confidence": dept_conf,
        "sentiment": sentiment,
        "sentiment_confidence": sent_conf,
        "priority": priority,
        "priority_confidence": prio_conf,
        "keywords": keywords,
        "locations": locations,
        "clean_text": clean_text,
    }


def analyze_batch(transcripts: list) -> list:
    return [analyze_transcript(t) for t in transcripts]
