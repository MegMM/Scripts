# single process hash compare

import hashlib
import os
from pathlib import Path, WindowsPath

def compute_file_hash(file_path, hash_algorithm=hashlib.sha256):
    hasher = hash_algorithm()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_unique_files(root_directory, extensions):
    unique_files = {}
    for root, _, files in os.walk(root_directory):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in extensions:
                file_hash = compute_file_hash(file_path)
                if file_hash not in unique_files:
                    unique_files[file_hash] = file_path
    return list(unique_files.values())

def save_unique_files(unique_files, save_file_path):
    with open(save_file_path, 'w') as f:
        for file_path in unique_files:
            f.write(f"{file_path}\n")

# Usage
root_directory = WindowsPath(r"C:\Users\megha\OneDrive\Calibre Libraries")
save_unique_files_list = WindowsPath(r"C:\MyProjects\Scripts\book_list_file.txt")
duplicate_files = WindowsPath(r"C:\MyProjects\Scripts\duplicates.txt")
extensions = ['.doc', '.mobi', '.zip', '.docx', '.azw3', '.azw', '.pdf', '.epub', '.txt', '.rtf', '.lit', '.kfx', '.original_mobi', '.pdb', '.htm', '.html', '.kfx-zip', '.prc', '.pdr', '.cbz', '.md', '.htmlz', '.tan', '.azw4', '.aax', '.original_epub']

unique_files = get_unique_files(root_directory, extensions)
save_unique_files(unique_files, save_unique_files_list)
