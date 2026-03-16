from flask import Flask, jsonify, request
import platform
import sys
import os
from datetime import datetime, timezone

import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)

model = None
target_names = None


def get_model():
    global model, target_names
    if model is None:
        iris = load_iris()
        target_names = iris.target_names.tolist()
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(iris.data, iris.target)
    return model, target_names


@app.route("/")
def hello():
    return jsonify({
        "message": "Hello from Hummingbird!",
        "runtime": f"Python {sys.version}",
        "platform": platform.system(),
        "ml_backend": f"scikit-learn {__import__('sklearn').__version__}",
        "numpy_version": np.__version__,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/predict", methods=["POST"])
def predict():
    """Predict Iris species from sepal/petal measurements.

    Expects JSON: {"features": [sepal_length, sepal_width, petal_length, petal_width]}
    """
    data = request.get_json(force=True)
    features = data.get("features")
    if not features or len(features) != 4:
        return jsonify({"error": "Provide 'features' array with 4 values: "
                        "[sepal_length, sepal_width, petal_length, petal_width]"}), 400

    clf, names = get_model()
    X = np.array(features).reshape(1, -1)
    prediction = clf.predict(X)[0]
    probabilities = clf.predict_proba(X)[0]

    return jsonify({
        "prediction": names[prediction],
        "confidence": round(float(probabilities.max()), 4),
        "probabilities": {name: round(float(p), 4)
                          for name, p in zip(names, probabilities)},
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


@app.route("/predict/sample")
def predict_sample():
    """Run prediction on a sample Iris input for quick testing."""
    clf, names = get_model()
    sample = np.array([[5.1, 3.5, 1.4, 0.2]])
    prediction = clf.predict(sample)[0]
    probabilities = clf.predict_proba(sample)[0]

    return jsonify({
        "input": {"sepal_length": 5.1, "sepal_width": 3.5,
                  "petal_length": 1.4, "petal_width": 0.2},
        "prediction": names[prediction],
        "confidence": round(float(probabilities.max()), 4),
        "probabilities": {name: round(float(p), 4)
                          for name, p in zip(names, probabilities)}
    })
