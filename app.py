# app.py
import os
import re
import json
import sqlite3
from datetime import datetime
from urllib.parse import urlparse
from flask import Flask, request, jsonify, g
from flask_cors import CORS

# Optional ML imports (only used if model files exist)
model = None
vectorizer = None
try:
    import joblib
    # attempt loading model files if they exist
    if os.path.exists("model.pkl") and os.path.exists("vectorizer.pkl"):
        model = joblib.load("model.pkl")
        vectorizer = joblib.load("vectorizer.pkl")
    else:
        # support pipeline saved as model.pkl only (optional)
        if os.path.exists("model.pkl"):
            model = joblib.load("model.pkl")
            # vectorizer may be inside pipeline; keep vectorizer None
except Exception:
    model = None
    vectorizer = None

app = Flask(__name__)
CORS(app)

DB_PATH = os.environ.get("PS_DB", "scans.db")
KEYWORDS = ["login", "verify", "account", "update", "secure", "confirm", "bank", "signin", "password", "reset", "payment"]

# ------------------------
# DB helpers
# ------------------------
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH, check_same_thread=False)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    confidence INTEGER,
                    status TEXT,
                    reasons TEXT,
                    created_at TEXT
                  )''')
    db.execute('''CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    note TEXT,
                    created_at TEXT
                  )''')
    db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ------------------------
# heuristics
# ------------------------
def entropy_score(s: str):
    if not s:
        return 0.0
    from collections import Counter
    counts = Counter(s)
    probs = [c/len(s) for c in counts.values()]
    import math
    return - sum(p * math.log2(p) for p in probs)

def contains_unicode(s: str):
    return any(ord(c) > 127 for c in s)

def is_ip_host(host: str):
    return re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', host) is not None

# ------------------------
# analysis (ML + heuristics, but safe fallback)
# ------------------------
def analyze_url(url: str):
    reasons = []
    base_conf = 100.0

    if not url:
        return { "confidence": 0.0, "status": "Dangerous", "reasons":[{"title":"Invalid URL","detail":"Empty input"}] }

    lowered = url.lower()
    parsed = urlparse(url)
    host = parsed.hostname or url

    # heuristic: keywords
    found_kw = [k for k in KEYWORDS if k in lowered]
    if found_kw:
        reasons.append({"title":"Suspicious keywords","detail":f"Found: {', '.join(found_kw)}"})
        base_conf -= 15 * len(found_kw) / max(1, len(KEYWORDS))

    # heuristic: ip host
    if is_ip_host(host):
        reasons.append({"title":"Numeric IP host","detail":"Host appears to be an IP address (common in disposable phishing)."})
        base_conf -= 25

    # heuristic: unicode / homoglyph
    if contains_unicode(host):
        reasons.append({"title":"Non-ASCII / homoglyphs","detail":"Domain contains non-ASCII characters which may be used to impersonate brands."})
        base_conf -= 15

    # heuristic: length / entropy
    ent = entropy_score(lowered)
    if len(url) > 75 or ent > 3.5:
        reasons.append({"title":"High entropy/length","detail":f"length={len(url)}, entropy={ent:.2f}"})
        base_conf -= 12

    # heuristic: suspicious query params
    if parsed.query and re.search(r'(password|pwd|token|auth|session|ssn|card|cvv)', parsed.query, re.I):
        reasons.append({"title":"Suspicious params","detail":"URL contains parameters often used to collect credentials."})
        base_conf -= 18

    # clamp base_conf
    base_conf = max(0.0, min(100.0, base_conf))

    # If ML model available, combine with ML output; otherwise rely on heuristics
    final_conf = base_conf
    try:
        if model is not None:
            if vectorizer is not None:
                X = vectorizer.transform([url])
                if hasattr(model, "predict_proba"):
                    ml_prob = model.predict_proba(X)[0][1] * 100.0
                else:
                    pred = model.predict([url])[0]
                    ml_prob = 90.0 if pred == 1 else 20.0
            else:
                if hasattr(model, "predict_proba"):
                    ml_prob = model.predict_proba([url])[0][1] * 100.0
                else:
                    pred = model.predict([url])[0]
                    ml_prob = 90.0 if pred == 1 else 20.0
            final_conf = base_conf * 0.6 + ml_prob * 0.4
            reasons.append({"title":"ML included","detail":f"Local model contributed {ml_prob:.1f}% confidence."})
    except Exception:
        pass

    final_conf = round(max(0.0, min(100.0, final_conf)), 1)
    if final_conf >= 80:
        status = "Safe"
    elif final_conf >= 50:
        status = "Suspicious"
    else:
        status = "Dangerous"

    # persist
    try:
        db = get_db()
        db.execute("INSERT INTO scans (url, confidence, status, reasons, created_at) VALUES (?, ?, ?, ?, ?)",
                   (url, int(final_conf), status, json.dumps(reasons), datetime.utcnow().isoformat()))
        db.commit()
    except Exception:
        pass

    return {"confidence": final_conf, "status": status, "reasons": reasons, "ml_available": model is not None}

# ------------------------
# routes
# ------------------------
@app.route("/scan", methods=["POST"])
def scan_route():
    init_db()
    data = request.get_json(force=True)
    url = data.get("url")
    result = analyze_url(url)
    return jsonify(result)

@app.route("/report", methods=["POST"])
def report_route():
    init_db()
    data = request.get_json(force=True)
    url = data.get("url")
    note = data.get("note", "")
    try:
        db = get_db()
        db.execute("INSERT INTO reports (url, note, created_at) VALUES (?, ?, ?)", (url, note, datetime.utcnow().isoformat()))
        db.commit()
        return jsonify({"status":"ok"}), 201
    except Exception as e:
        return jsonify({"status":"error", "error": str(e)}), 500

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
