# phishshield
A lightweight hybrid phishing detector combining explainable heuristics with a compact ML model. Provides a real-time Detection Confidence score with transparent reasons and integrates easily as a web UI, browser extension, or API. (Demo + prototype for CodeRift hackathon.)

Files:
- frontend.html
- app.py
- model.pkl (create with model_train.py)
- vectorizer.pkl (create with model_train.py)
- model_train.py
- requirements.txt
- scans.db (created at runtime)

# Quick start (Windows / Linux / macOS)
1. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows

2. Install dependencies:
   pip install -r requirements.txt

3. Train the demo model (creates model.pkl and vectorizer.pkl):
   python model_train.py

4. Run the backend:
   python app.py

5. Open frontend:
   - Option A: double-click frontend.html to open in browser (frontend expects backend at http://localhost:5000)
   - Option B: serve it via a static server:
       python -m http.server 8000
     then visit http://localhost:8000/frontend.html

6. Use cases:
   - Enter test URLs (safe / suspicious / dangerous examples) and click Check.
   - The frontend will display "Detection Confidence: xx% (Status)" and list reasons.

Create final ZIP (optional):
- From the folder containing files, run:
  zip -r PhishShield_Final.zip frontend.html app.py model.pkl vectorizer.pkl requirements.txt README.md model_train.py
  (Windows: use 7-zip or `tar -a -c -f PhishShield_Final.zip <files>`)

# Security:
- The backend does not visit target URLs; it only analyzes the string and optionally calls WHOIS or VirusTotal if enabled.
- If you enable VirusTotal, be mindful of API limits/terms.

### --->TLDR /Exact Commands to run locally

## INSTALLTION ON WINDOWS
# 1. clone repo
git clone https://github.com/your-username/PhishShield.git
cd PhishShield

# 2. create & activate venv
python -m venv venv
venv\Scripts\activate

# 3. install deps
pip install -r requirements.txt

# 4a. (optional) create model of your own
python model_train.py   # creates model.pkl + vectorizer.pkl

# 4b. run backend
python app.py

# 5. open frontend
Option 1: double-click frontend.html
Option 2 (serve static):
python -m http.server 8000
visit: http://localhost:8000/frontend.html

## INSTALLATION ON LINUX/MACOS
git clone https://github.com/your-username/PhishShield.git
cd PhishShield

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# optional train
python model_train.py

# run backend
python app.py

# serve frontend
python3 -m http.server 8000
visit http://localhost:8000/frontend.html

