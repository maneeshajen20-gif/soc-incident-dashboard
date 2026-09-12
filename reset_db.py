import sqlite3
import shutil
import os

def reset_system():
    # 1. Clear all database tables
    conn = sqlite3.connect('soc_tool.db')
    tables = ['incidents', 'evidence', 'timeline', 'iocs']
    
    for table in tables:
        try:
            conn.execute(f'DELETE FROM {table}')
        except sqlite3.OperationalError:
            pass # Skips if table somehow doesn't exist
            
    conn.commit()
    conn.close()
    print("[+] Database wiped clean.")

    # 2. Delete the physical evidence files
    if os.path.exists('evidence'):
        shutil.rmtree('evidence')
        print("[+] Evidence folder deleted.")
        
    print("[+] System reset successful. Ready for a fresh start.")

if __name__ == '__main__':
    # Confirm before wiping
    confirm = input("This will delete ALL incidents and evidence. Type 'yes' to continue: ")
    if confirm.lower() == 'yes':
        reset_system()
    else:
        print("Reset cancelled.")
