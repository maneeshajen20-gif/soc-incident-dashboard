from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import sqlite3
import os
import hashlib
import evidence_collector  
import integrity
import report_generator 
from datetime import datetime

app = Flask(__name__)
app.secret_key = "soc_secure_key_123" # Required for flash messages

def get_db_connection():
    conn = sqlite3.connect('soc_tool.db')
    conn.row_factory = sqlite3.Row  
    return conn

def log_timeline(incident_id, event):
    conn = get_db_connection()
    conn.execute('INSERT INTO timeline (incident_id, event) VALUES (?, ?)', (incident_id, event))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    incidents = conn.execute('SELECT * FROM incidents ORDER BY rowid DESC').fetchall()
    
    # Dashboard Statistics
    stats = {
        'total': len(incidents),
        'high_severity': sum(1 for i in incidents if i['severity'] in ['HIGH', 'CRITICAL']),
        'investigating': sum(1 for i in incidents if i['status'] == 'INVESTIGATING'),
        'resolved': sum(1 for i in incidents if i['status'] == 'RESOLVED')
    }
    conn.close()
    return render_template('index.html', incidents=incidents, stats=stats)

@app.route('/add', methods=['POST'])
def add_incident():
    incident_id = request.form['incident_id']
    title = request.form['title']
    severity = request.form['severity']
    status = request.form['status']
    description = request.form['description']
    
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO incidents (incident_id, title, severity, status, description) 
            VALUES (?, ?, ?, ?, ?)
        ''', (incident_id, title, severity, status, description))
        conn.commit()
        log_timeline(incident_id, f"Incident created: {title}")
        log_timeline(incident_id, f"Status set to {status}")
        flash(f"✓ Incident {incident_id} created successfully.", "success")
    except sqlite3.IntegrityError:
        flash(f"⚠ Error: Incident {incident_id} already exists.", "error")
    conn.close()
    return redirect(url_for('index'))

@app.route('/collect/<incident_id>')
def collect_evidence(incident_id):
    log_timeline(incident_id, "Evidence collection initiated.")
    folder_path = evidence_collector.run_collection(incident_id)
    integrity.create_manifest(folder_path)
    
    # Parse manifest and store in DB for future verification
    manifest_path = os.path.join(folder_path, "manifest.txt")
    if os.path.exists(manifest_path):
        conn = get_db_connection()
        with open(manifest_path, 'r') as f:
            for line in f:
                if "|" in line:
                    parts = line.strip().split(" | SHA-256: ")
                    filename = parts[0]
                    file_hash = parts[1]
                    conn.execute('INSERT INTO evidence (incident_id, filename, original_sha256) VALUES (?, ?, ?)', 
                                 (incident_id, filename, file_hash))
        conn.commit()
        conn.close()

    log_timeline(incident_id, "Evidence collection completed and SHA-256 hashes generated.")
    flash("✓ Evidence collection completed successfully.", "success")
    return redirect(url_for('view_incident', incident_id=incident_id))

@app.route('/incident/<incident_id>')
def view_incident(incident_id):
    conn = get_db_connection()
    incident = conn.execute('SELECT * FROM incidents WHERE incident_id = ?', (incident_id,)).fetchone()
    timeline = conn.execute('SELECT * FROM timeline WHERE incident_id = ? ORDER BY timestamp ASC', (incident_id,)).fetchall()
    iocs = conn.execute('SELECT * FROM iocs WHERE incident_id = ?', (incident_id,)).fetchall()
    evidence = conn.execute('SELECT * FROM evidence WHERE incident_id = ?', (incident_id,)).fetchall()
    conn.close()

    if incident is None:
        return "Incident not found", 404

    # Calculate Evidence Stats
    verified = sum(1 for e in evidence if e['status'] == 'VERIFIED')
    compromised = sum(1 for e in evidence if e['status'] == 'COMPROMISED')

    return render_template('view.html', incident=incident, timeline=timeline, iocs=iocs, evidence=evidence, verified=verified, compromised=compromised)

@app.route('/update_status/<incident_id>', methods=['POST'])
def update_status(incident_id):
    new_status = request.form['status']
    conn = get_db_connection()
    old_status_row = conn.execute('SELECT status FROM incidents WHERE incident_id = ?', (incident_id,)).fetchone()
    old_status = old_status_row['status'] if old_status_row else "UNKNOWN"
    
    if new_status != old_status:
        conn.execute('UPDATE incidents SET status = ? WHERE incident_id = ?', (new_status, incident_id))
        conn.commit()
        log_timeline(incident_id, f"Status changed from {old_status} to {new_status}")
        flash(f"✓ Status updated to {new_status}.", "success")
    conn.close()
    return redirect(url_for('view_incident', incident_id=incident_id))

@app.route('/add_ioc/<incident_id>', methods=['POST'])
def add_ioc(incident_id):
    ioc_type = request.form['ioc_type']
    value = request.form['value']
    description = request.form['description']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO iocs (incident_id, ioc_type, value, description) VALUES (?, ?, ?, ?)', 
                 (incident_id, ioc_type, value, description))
    conn.commit()
    conn.close()
    
    log_timeline(incident_id, f"IOC Added [{ioc_type}]: {value}")
    flash("✓ IOC recorded successfully.", "success")
    return redirect(url_for('view_incident', incident_id=incident_id))

@app.route('/verify/<incident_id>')
def verify_evidence(incident_id):
    conn = get_db_connection()
    evidence_records = conn.execute('SELECT * FROM evidence WHERE incident_id = ?', (incident_id,)).fetchall()
    
    evidence_dir = "evidence"
    target_folder = None
    if os.path.exists(evidence_dir):
        for folder in os.listdir(evidence_dir):
            if folder.startswith(incident_id):
                target_folder = os.path.join(evidence_dir, folder)
                break
                
    if not target_folder:
        flash("⚠ No evidence folder found to verify.", "error")
        return redirect(url_for('view_incident', incident_id=incident_id))

    all_verified = True
    for record in evidence_records:
        file_path = os.path.join(target_folder, record['filename'])
        current_status = 'COMPROMISED'
        
        if os.path.exists(file_path):
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                hasher.update(f.read())
            current_hash = hasher.hexdigest()
            
            if current_hash == record['original_sha256']:
                current_status = 'VERIFIED'
            else:
                all_verified = False
        else:
            all_verified = False # File is missing

        conn.execute('UPDATE evidence SET status = ? WHERE id = ?', (current_status, record['id']))

    conn.commit()
    conn.close()

    if all_verified:
        log_timeline(incident_id, "Evidence integrity check passed. All hashes verified.")
        flash("✓ All evidence files verified successfully.", "success")
    else:
        log_timeline(incident_id, "ALERT: Evidence integrity check FAILED. File modification detected.")
        flash("⚠ Evidence integrity check failed. Some files have been modified.", "error")

    return redirect(url_for('view_incident', incident_id=incident_id))

@app.route('/report/<incident_id>')
def generate_report_route(incident_id):
    conn = get_db_connection()
    incident = conn.execute('SELECT * FROM incidents WHERE incident_id = ?', (incident_id,)).fetchone()
    timeline = conn.execute('SELECT * FROM timeline WHERE incident_id = ? ORDER BY timestamp ASC', (incident_id,)).fetchall()
    iocs = conn.execute('SELECT * FROM iocs WHERE incident_id = ?', (incident_id,)).fetchall()
    evidence = conn.execute('SELECT * FROM evidence WHERE incident_id = ?', (incident_id,)).fetchall()
    conn.close()

    if incident is None:
        flash("⚠ Incident not found.", "error")
        return redirect(url_for('index'))

    try:
        # Pass DB data to the generator
        pdf_path = report_generator.generate_pdf(incident, evidence, iocs, timeline)
        log_timeline(incident_id, "Professional Incident PDF Report generated.")
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        flash(f"⚠ Error generating report: {str(e)}", "error")
        return redirect(url_for('view_incident', incident_id=incident_id))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
