import os
import subprocess
from datetime import datetime

def create_evidence_dir(incident_id):
    # Creates a timestamped folder inside your 'evidence' directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"evidence/{incident_id}_{timestamp}"
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

def collect_command_output(command, filename, folder_path):
    file_path = os.path.join(folder_path, filename)
    try:
        # Execute the Linux command and capture the output
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Save the captured text into a file
        with open(file_path, 'w') as f:
            f.write(result.stdout)
            # If the command generates an error, log that too
            if result.stderr:
                f.write("\n--- Errors ---\n" + result.stderr)
        print(f"[+] Collected: {filename}")
    except Exception as e:
        print(f"[-] Failed to collect {filename}: {e}")

def run_collection(incident_id):
    print(f"Starting evidence collection for {incident_id}...")
    folder = create_evidence_dir(incident_id)
    
    # Core SOC Evidence Commands
    collect_command_output("uname -a", "system_info.txt", folder)
    collect_command_output("whoami", "current_user.txt", folder)
    collect_command_output("ps aux", "running_processes.txt", folder)
    collect_command_output("ss -tulnp", "network_connections.txt", folder)
    
    print(f"Collection complete. Files saved in: {folder}")
    return folder

if __name__ == '__main__':
    # Test the collector using our mock incident ID
    run_collection("INC-001")
