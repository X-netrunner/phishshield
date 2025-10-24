# phishshield
This is a project prototype done for an hackthon ( CodeRift ) hosted by Unstop.

Files:
- frontend.html
- app.py
- model.pkl (create with model_train.py)
- vectorizer.pkl (create with model_train.py)
- model_train.py
- requirements.txt
- scans.db (created at runtime)

Quick start (Windows / Linux / macOS)
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

Security:
- The backend does not visit target URLs; it only analyzes the string and optionally calls WHOIS or VirusTotal if enabled.
- If you enable VirusTotal, be mindful of API limits/terms.

