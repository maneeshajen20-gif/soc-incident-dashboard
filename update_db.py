import sqlite3
from datetime import datetime

def upgrade_database():
    conn = sqlite3.connect('soc_tool.db')
    c = conn.cursor()

    # Timeline Table
    c.execute('''CREATE TABLE IF NOT EXISTS timeline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event TEXT
                )''')

    # IOC Table
    c.execute('''CREATE TABLE IF NOT EXISTS iocs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id TEXT,
                    ioc_type TEXT,
                    value TEXT,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')

    # Evidence Tracking Table
    c.execute('''CREATE TABLE IF NOT EXISTS evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id TEXT,
                    filename TEXT,
                    original_sha256 TEXT,
                    status TEXT DEFAULT 'VERIFIED',
                    collected_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')

    conn.commit()
    conn.close()
    print("[+] Database expanded successfully with Timeline, IOC, and Evidence tables.")

if __name__ == "__main__":
    upgrade_database()
