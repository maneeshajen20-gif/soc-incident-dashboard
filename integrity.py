import hashlib
import os

def generate_sha256(file_path):
    # Initialize the SHA-256 hash object
    sha256_hash = hashlib.sha256()
    
    # Read the file in binary mode in small chunks
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            
    return sha256_hash.hexdigest()

def create_manifest(folder_path):
    manifest_path = os.path.join(folder_path, "manifest.txt")
    print(f"Generating evidence manifest for: {folder_path}")
    
    with open(manifest_path, "w") as manifest:
        # Loop through every file in your collected evidence folder
        for filename in os.listdir(folder_path):
            if filename == "manifest.txt":
                continue # Skip hashing the manifest itself
                
            file_path = os.path.join(folder_path, filename)
            
            # Ensure it is a file and calculate its hash
            if os.path.isfile(file_path):
                file_hash = generate_sha256(file_path)
                manifest_line = f"{filename} | SHA-256: {file_hash}\n"
                manifest.write(manifest_line)
                print(f"[+] Hashed: {filename}")
                
    print(f"Manifest saved to: {manifest_path}")

if __name__ == '__main__':
    # Testing the script on the exact folder your collector just created
    target_folder = "evidence/INC-001_20260903_091932" 
    
    # Check if the folder exists before running
    if os.path.exists(target_folder):
        create_manifest(target_folder)
    else:
        print(f"Error: Folder '{target_folder}' not found.")
