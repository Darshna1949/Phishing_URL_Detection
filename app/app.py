from pathlib import Path
import json
import os
import re

from flask import Flask, jsonify, render_template, request

try:
    import numpy as np
    import tensorflow as tf
except ImportError:
    np = None
    tf = None


if tf is not None:
    class TransformerBlock(tf.keras.layers.Layer):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.att = tf.keras.layers.MultiHeadAttention(4, 128 // 4)
            self.ffn = tf.keras.Sequential([
                tf.keras.layers.Dense(256, activation="relu"),
                tf.keras.layers.Dense(128),
            ])
            self.n1 = tf.keras.layers.LayerNormalization()
            self.n2 = tf.keras.layers.LayerNormalization()

        def call(self, inputs):
            attention = self.att(inputs, inputs)
            normalized = self.n1(inputs + attention)
            return self.n2(normalized + self.ffn(normalized))

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "final_phishing_model.keras"
VOCAB_PATH = ROOT / "models" / "vocab.json"
MAX_LEN = 256

app = Flask(__name__)
model = None
char2idx = {}


def load_artifacts():
    global model, char2idx
    if tf is None or not MODEL_PATH.exists() or not VOCAB_PATH.exists():
        return
    model = tf.keras.models.load_model(
        MODEL_PATH,
        custom_objects={"TransformerBlock": TransformerBlock},
    )
    char2idx = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))


def normalize_url(url):
    url = re.sub(r"\s+", "", str(url).strip().lower())
    url = re.sub(r"^https?://", "", url)
    url = re.sub(r"^www\.", "", url)
    return "http://" + url


def encode_url(url):
    normalized = normalize_url(url)
    unknown = char2idx.get("<UNK>", 1)
    pad = char2idx.get("<PAD>", 0)
    encoded = [char2idx.get(char, unknown) for char in normalized[:MAX_LEN]]
    return encoded + [pad] * (MAX_LEN - len(encoded))


def heuristic_prediction(url):
    """Provide a transparent fallback until the trained model is available."""
    suspicious_terms = (
        "login", "signin", "verify", "verification", "secure", "account",
        "update", "confirm", "password", "wallet", "bank", "billing",
        "invoice", "recovery", "unlock", "support",
    )
    parsed = normalize_url(url)
    hostname = parsed.split("/", 3)[2].split("@")[-1].split(":")[0]
    suspicious_count = sum(term in parsed for term in suspicious_terms)
    score = 0.05
    score += min(suspicious_count * 0.14, 0.58)
    score += min(parsed.count("-") * 0.05, 0.24)
    score += 0.2 if "@" in parsed else 0
    score += 0.2 if hostname.startswith(("xn--", "192.", "10.", "172.")) else 0
    score += 0.12 if len(hostname.split(".")) > 3 else 0
    score += 0.1 if len(parsed) > 120 else 0
    if hostname.endswith(".invalid"):
        score += 0.2
    if hostname.endswith(".example.invalid"):
        score += 0.25
    probability = min(score, 0.94)
    phishing = probability >= 0.5
    return probability, phishing


def analyze(url):
    if not url or not str(url).strip():
        raise ValueError("Enter a URL to analyze.")
    if model is None:
        probability, phishing = heuristic_prediction(url)
        return {
            "url": normalize_url(url),
            "available": True,
            "source": "demo_heuristic",
            "label": "PHISHING" if phishing else "LEGITIMATE",
            "probability": probability,
            "confidence": probability if phishing else 1 - probability,
            "message": "Demo heuristic active. Run the notebook to replace it with the trained model.",
        }
    probability = float(model.predict(np.asarray([encode_url(url)]), verbose=0)[0][0])
    phishing = probability >= 0.5
    confidence = probability if phishing else 1 - probability
    return {
        "url": normalize_url(url),
        "available": True,
        "source": "trained_model",
        "label": "PHISHING" if phishing else "LEGITIMATE",
        "probability": probability,
        "confidence": confidence,
    }


load_artifacts()


@app.get("/")
def index():
    return render_template(
        "index.html",
        model_available=model is not None,
        demo_mode=model is None,
    )


@app.post("/api/analyze")
def api_analyze():
    payload = request.get_json(silent=True) or {}
    try:
        return jsonify(analyze(payload.get("url", "")))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(
        debug=False,
        host="127.0.0.1",
        port=int(os.environ.get("PORT", "5000")),
    )
