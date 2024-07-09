import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib

def compute_file_hash(file_path):
    # Implement your file hash computation logic here
    # For example, using SHA-1:
    with open(file_path, 'rb') as f:
        file_hash = hashlib.sha1(f.read()).hexdigest()
    return file_hash, file_path

def get_unique_and_duplicate_files(root_directory, extensions, max_workers=8):
    unique_files = {}
    duplicate_files = {}

    for root, _, files in os.walk(root_directory):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in extensions:
                file_hash, _ = compute_file_hash(file_path)
                if file_hash not in unique_files:
                    unique_files[file_hash] = file_path
                else:
                    # Collision: Duplicate file
                    duplicate_files.setdefault(file_hash, []).append(file_path)

    # Separate unique and duplicate files
    unique_list = list(unique_files.values())
    duplicate_list = [duplicates for duplicates in duplicate_files.values()]

    return unique_list, duplicate_list

# Example usage:
root_dir = '/path/to/your/directory'
file_extensions = ['.txt', '.jpg', '.png']  # Add your desired extensions
unique_files, duplicate_files = get_unique_and_duplicate_files(root_dir, file_extensions)

print("Unique files:")
for file_path in unique_files:
    print(file_path)

print("\nDuplicate files:")
for duplicates in duplicate_files:
    for file_path in duplicates:
        print(file_path)
