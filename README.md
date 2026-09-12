# SOC Incident Dashboard

A clean, easy-to-use web dashboard built with Python and Flask to help security teams track alerts, collect evidence, and generate reports. 

### What It Does
* **Track Incidents:** Log security alerts and manage them on a clean dashboard.
* **Collect & Verify Evidence:** Automatically captures system data and uses SHA-256 hashing to prove the evidence hasn't been tampered with.
* **Generate PDF Reports:** Click a button to instantly download a professional timeline and evidence report.

### Built With
* Backend: Python, Flask, SQLite
* Frontend: HTML, Custom CSS
* Tools: Hashlib (SHA-256), FPDF (PDF Generation)

### How to Run It

**1. Download the code:**
* `git clone https://github.com/maneeshajen20-gif/soc-incident-dashboard.git`
* `cd soc-incident-dashboard`

**2. Set up your environment:**
* `python3 -m venv venv`
* `source venv/bin/activate`
* `pip install -r requirements.txt`

**3. Start the database and app:**
* `python reset_db.py`
* `python app.py`

Open http://127.0.0.1:5000 in your web browser.
