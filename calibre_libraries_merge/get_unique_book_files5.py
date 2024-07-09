# copies the unique files but retains the library structure

import hashlib
import os
from pathlib import Path, WindowsPath
from shutil import copy2
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

    return get_unique_duplicate_files(all_files, list(unique_files.values()))

def get_unique_duplicate_files(all_files, unique_files):
    all_files = [WindowsPath(f) for f in all_files]
    unique_files = [WindowsPath(f) for f in unique_files]
    return unique_files, list(set(all_files) - set(unique_files))

def save_list_to_file(save_list, save_file):
    with open(save_file, 'w') as f:
        for file_path in save_list:
            f.write(f"{file_path}\n")

def get_most_recent_copies(file_paths):
    most_recent_files = {}
    for file_path in file_paths:
        base_name, _ = os.path.splitext(os.path.basename(file_path))
        file_date = os.path.getmtime(file_path)
        if base_name not in most_recent_files or file_date > most_recent_files[base_name]:
            most_recent_files[base_name] = file_date

    # Extract the most recent file paths
    result = [file_path for base_name, _ in most_recent_files.items() for file_path in file_paths if base_name in file_path]
    return result

# Example usage:
# all_file_paths = [...]  # Your list of file paths
# most_recent_copies = get_most_recent_files(all_file_paths)
# print(most_recent_copies)



### original copied to retain directory structure
# def copy_unique_files(unique_files, root_directory, new_root_directory):
#     for file_path in unique_files:
#         relative_path = file_path.relative_to(root_directory)
#         new_file_path = new_root_directory / relative_path
        
#         # Create the parent directories if they don't exist
#         new_file_path.parent.mkdir(parents=True, exist_ok=True)
        
#         # Copy the file
#         copy2(file_path, new_file_path)


# ONLY copying unique files to one directory     
def copy_unique_files(unique_files, new_directory):
    new_directory.parent.mkdir(parents=True, exist_ok=True)
    for file_path in unique_files:
        # Copy the file
        new_path = new_directory/(WindowsPath(file_path)).name
        if not new_path:
            print(new_path)
            # copy2(file_path, new_path)

# Usage
root_directory = WindowsPath(r"C:\Users\megha\OneDrive\Calibre Libraries")
new_root_directory = WindowsPath(r"C:\Calibre Library\onedrive_unique_files")
save_uniques_file = WindowsPath(r"C:\MyProjects\Scripts\uniques_file.txt")
save_duplicates_file = WindowsPath(r"C:\MyProjects\Scripts\duplicates_file.txt")
extensions = ['.doc', '.mobi', '.zip', '.docx', '.azw3', '.azw', '.pdf', '.epub', '.txt', '.rtf', '.lit', '.kfx', '.original_mobi', '.pdb', '.htm', '.html', '.kfx-zip', '.prc', '.pdr', '.cbz', '.md', '.htmlz', '.tan', '.azw4', '.aax', '.original_epub']

unique_files = []
duplicates_files = []

with open(save_uniques_file, 'r') as suf:
    unique_files = [line.rstrip() for line in suf]
with open(save_duplicates_file, 'r') as sdf:
    duplicates_files = [line.rstrip() for line in sdf]

# out of synch
if not unique_files or not duplicates_files:
    print(f"Running parallel hashing compare on {root_directory = }")
    # Get the list of unique files
    unique_files, duplicate_files = get_unique_files_parallel(root_directory, extensions)
    save_list_to_file(unique_files, save_uniques_file)
    save_list_to_file(duplicate_files, save_duplicates_file)
    
else:
    print(f"Using saves files...")

print(f"Copying {len(unique_files) = }")
print(f"Copying most likely correct duplicate {len(duplicates_files) = }")
# Copy unique files to the new directory, maintaining structure
# copy_unique_files(unique_files, new_root_directory)
