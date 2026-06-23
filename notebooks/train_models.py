"""
CitizenVoice AI - Model Training Script

Trains three TF-IDF + Logistic Regression pipelines on the synthetic
conversations dataset:
    1. classifier.pkl  -> predicts responsible department from transcript
    2. sentiment.pkl   -> predicts sentiment (Positive/Neutral/Negative)
    3. priority.pkl    -> predicts priority (Low/Medium/High/Critical)

Run:  python notebooks/train_models.py
Requires: data/conversations.csv (run generate_dataset.py first)
Outputs: models/classifier.pkl, models/sentiment.pkl, models/priority.pkl
"""

import os
import sys
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.preprocessing import preprocess_for_vectorizer

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DATA_PATH = os.path.join(BASE_DIR, "data", "conversations.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")


def build_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(max_features=3000, ngram_range=(1, 2), min_df=2)),
        ("clf", LogisticRegression(max_iter=1000, C=5.0, class_weight="balanced")),
    ])


def train_and_save(X_train, X_test, y_train, y_test, label_name, out_path):
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"\n=== {label_name} model ===")
    print(f"Accuracy: {acc:.3f}")
    print(classification_report(y_test, preds, zero_division=0))
    joblib.dump(pipeline, out_path)
    print(f"Saved -> {out_path}")
    return acc


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)
    df = pd.read_csv(DATA_PATH)
    df["clean_text"] = df["transcript"].apply(preprocess_for_vectorizer)

    X = df["clean_text"]

    results = {}

    # 1. Department classifier
    X_train, X_test, y_train, y_test = train_test_split(
        X, df["department"], test_size=0.2, random_state=42, stratify=df["department"]
    )
    results["department"] = train_and_save(
        X_train, X_test, y_train, y_test,
        "Department Classifier", os.path.join(MODELS_DIR, "classifier.pkl")
    )

    # 2. Sentiment classifier
    X_train, X_test, y_train, y_test = train_test_split(
        X, df["sentiment"], test_size=0.2, random_state=42, stratify=df["sentiment"]
    )
    results["sentiment"] = train_and_save(
        X_train, X_test, y_train, y_test,
        "Sentiment Classifier", os.path.join(MODELS_DIR, "sentiment.pkl")
    )

    # 3. Priority classifier
    X_train, X_test, y_train, y_test = train_test_split(
        X, df["priority"], test_size=0.2, random_state=42, stratify=df["priority"]
    )
    results["priority"] = train_and_save(
        X_train, X_test, y_train, y_test,
        "Priority Classifier", os.path.join(MODELS_DIR, "priority.pkl")
    )

    print("\n=== Summary ===")
    for k, v in results.items():
        print(f"{k}: accuracy = {v:.3f}")


if __name__ == "__main__":
    main()
