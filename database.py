import sqlite3

def init_db():
    # Connects to a local database file (creates it if it doesn't exist)
    conn = sqlite3.connect('soc_tool.db')
    cursor = conn.cursor()
    
    # Creates the incidents table based on your project requirements
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT UNIQUE,
            title TEXT,
            severity TEXT,
            status TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
