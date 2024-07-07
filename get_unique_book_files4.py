# parallel hash processing just based on directory structure

import hashlib
import os
from pathlib import Path, WindowsPath
from concurrent.futures import ThreadPoolExecutor, as_completed

def compute_file_hash(file_path, hash_algorithm=hashlib.sha256):
    hasher = hash_algorithm()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest(), file_path

def get_unique_files_parallel(root_directory, extensions, max_workers=8):
    unique_files = {}
    all_files = []
    
    for root, _, files in os.walk(root_directory):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in extensions:
                all_files.append(file_path)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(compute_file_hash, file): file for file in all_files}
        for future in as_completed(future_to_file):
            try:
                file_hash, file_path = future.result()
                if file_hash not in unique_files:
                    unique_files[file_hash] = file_path
            except Exception as exc:
                print(f"File {future_to_file[future]} generated an exception: {exc}")
    
    # return list(unique_files.values())
    unique_files_list = list(WindowsPath(unique_files.values()))
    duplicate_files = get_duplicates_from_list(all_files, unique_files_list)
    return unique_files_list, duplicate_files

def get_duplicates_from_list(all_files, unique_files):
    all_files = [WindowsPath(f) for f in all_files]
    return list(set(all_files) - set(unique_files))

def save_unique_files(unique_files, save_file_path):
    with open(save_file_path, 'w') as f:
        for file_path in unique_files:
            f.write(f"{file_path}\n")

# # Usage
# root_directory = Path('/path/to/root')
# extensions = {'.format1', '.format2'}  # Add all relevant extensions
# unique_files = get_unique_files_parallel(root_directory, extensions)

# save_file_path = Path("/path/to/directory/unique_books.txt")
# save_unique_files(unique_files, save_file_path)


root_directory = WindowsPath(r"C:\Users\megha\OneDrive\Calibre Libraries")
save_unique_files_list = WindowsPath(r"C:\MyProjects\Scripts\book_list_file.txt")
duplicate_files = WindowsPath(r"C:\MyProjects\Scripts\duplicates.txt")
extensions = ['.doc', '.mobi', '.zip', '.docx', '.azw3', '.azw', '.pdf', '.epub', '.txt', '.rtf', '.lit', '.kfx', '.original_mobi', '.pdb', '.htm', '.html', '.kfx-zip', '.prc', '.pdr', '.cbz', '.md', '.htmlz', '.tan', '.azw4', '.aax', '.original_epub']

unique_files = get_unique_files_parallel(root_directory, extensions)
save_unique_files(unique_files, save_unique_files_list)
save_duplicate_files()