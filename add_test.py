import sqlite3

# Connect to the database
conn = sqlite3.connect('soc_tool.db')
cursor = conn.cursor()

# Insert a fake SSH brute force incident
cursor.execute('''
    INSERT INTO incidents (incident_id, title, severity, status, description) 
    VALUES ('INC-001', 'SSH Brute Force', 'HIGH', 'NEW', 'Multiple failed SSH logins detected from external IP.')
''')

# Save and close
conn.commit()
conn.close()
print("Test incident added to database!")
