from fpdf import FPDF
import os
from datetime import datetime

def generate_pdf(incident, evidence, iocs, timeline):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="SOC INCIDENT RESPONSE REPORT", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.ln(10)
    
    # 1. Incident Overview
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 8, txt="1. INCIDENT OVERVIEW", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 6, txt=f"ID: {incident['incident_id']}", ln=True)
    pdf.cell(200, 6, txt=f"Title: {incident['title']}", ln=True)
    pdf.cell(200, 6, txt=f"Severity: {incident['severity']}", ln=True)
    pdf.cell(200, 6, txt=f"Final Status: {incident['status']}", ln=True)
    pdf.multi_cell(0, 6, txt=f"Description: {incident['description']}")
    pdf.ln(5)
    
    # 2. Indicators of Compromise (IOCs)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 8, txt="2. INDICATORS OF COMPROMISE", ln=True)
    pdf.set_font("Arial", size=10)
    if not iocs:
        pdf.cell(200, 6, txt="No IOCs recorded.", ln=True)
    else:
        for ioc in iocs:
            pdf.cell(200, 6, txt=f"- [{ioc['ioc_type']}] {ioc['value']} : {ioc['description']}", ln=True)
    pdf.ln(5)

    # 3. Evidence & Integrity
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 8, txt="3. EVIDENCE & INTEGRITY MANIFEST", ln=True)
    pdf.set_font("Arial", size=9)
    if not evidence:
        pdf.cell(200, 6, txt="No evidence collected.", ln=True)
    else:
        # Table Header
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(50, 6, txt="Filename", border=1)
        pdf.cell(110, 6, txt="Original SHA-256", border=1)
        pdf.cell(30, 6, txt="Status", border=1, ln=True)
        # Table Rows
        pdf.set_font("Arial", size=8)
        for ev in evidence:
            pdf.cell(50, 6, txt=ev['filename'], border=1)
            pdf.cell(110, 6, txt=ev['original_sha256'], border=1)
            pdf.cell(30, 6, txt=ev['status'], border=1, ln=True)
    pdf.ln(8)

    # 4. Investigation Timeline
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 8, txt="4. CHRONOLOGICAL TIMELINE", ln=True)
    pdf.set_font("Arial", size=9)
    if not timeline:
        pdf.cell(200, 6, txt="No timeline events.", ln=True)
    else:
        for event in timeline:
            pdf.multi_cell(0, 6, txt=f"[{event['timestamp']}] {event['event']}")

    # Save to evidence folder
    folder_path = os.path.join("evidence", incident['incident_id'])
    os.makedirs(folder_path, exist_ok=True)
    
    report_filename = f"{incident['incident_id']}_Report.pdf"
    report_path = os.path.join(folder_path, report_filename)
    
    pdf.output(report_path)
    return report_path
