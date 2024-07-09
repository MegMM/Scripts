###

# Reads through slightly corrupted Calibre libaries to find authors and books, and files. 

# TODO: Copy all files to a directory. Renames any files with same info numerically.
# TODO: Stores info to CSV file.

###

import os, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import filecmp
import hashlib
from pathlib import WindowsPath, Path
import pandas as pd
import pickle
from functools import reduce
import operator

dirs = WindowsPath(r"C:\Users\megha\OneDrive\Calibre Libraries")
# level 0: overall home directory
# level 1: individual library directories
# level 2: author directories
# level 3: book directories
# level 4: book digital files


extensions = ['.doc', '.mobi', '.zip', '.docx', '.azw3', '.azw', '.pdf', '.epub', '.txt', '.rtf', '.lit', '.kfx', '.original_mobi', '.pdb', '.htm', '.html', '.kfx-zip', '.prc', '.pdr', '.cbz', '.md', '.htmlz', '.tan', '.azw4', '.aax', '.original_epub']
def get_extensions(file):
    if file.is_file():
        if file.suffix not in extensions:
            extensions.append(file.suffix)

root = [p for p in dirs.iterdir() if p.is_dir()]


class Library:
    def __init__(self, path):
        if path and isinstance(path, Path):
            self.path = path
            self.name = self.path.stem
            self.author_paths = []
            self.book_files = []
            self.book_dirs = []
            self.get_author_paths()
            self.get_book_dirs()
            self.get_book_dirs()

    def get_author_paths(self):
        self.author_paths = [a for a in self.path.iterdir() if a.is_dir() and 'calnote' not in a.stem]

    def get_book_dirs(self):
        self.book_dirs = [b for p in self.author_paths for b in p.iterdir() if b.is_dir()]

    def get_ebook_files(self):
        for dir in self.book_dirs:
            if dir.is_dir():
                files = [f for f in dir.iterdir() if f.suffix in extensions]
                self.book_files.extend(files)

def save_list_to_file(items_list, save_file):
    with open(save_file, 'wb') as f:
        pickle.dump(items_list, f)

def get_list_from_file(save_file):
    with open (save_file, 'rb') as fp:
        return pickle.load(fp)

def normalize_path(path):
    if os.name == 'nt':  # Check if the OS is Windows
        return f"\\\\?\\{str(path)}"
    return path

def file_compare_method(file_paths):
    unique_paths = []
    duplicates = []

    print(f"{type(file_paths) = }, {len(file_paths)}")
    for path in file_paths:
        is_duplicate = False
        normalized_path = normalize_path(path)
        # print(f"{normalized_path = }")
        for file in unique_paths:
            normalized_file = normalize_path(file)
            # if len(normalized_file) > 260:
            #     print(f"{normalized_file = }")
                # print(normalized_file)
            # print(f"Comparing file: {normalized_file}")
            if filecmp.cmp(normalized_path, normalized_file, shallow=True):
                # print(f"{file} is duplicate")
                duplicates.append(path)
                is_duplicate = True
                break
        if not is_duplicate:
            # print(f"{path} is unique")
            unique_paths.append(path)

    return unique_paths, duplicates

def calculate_hash(file_path, hash_algorithm=hashlib.md5, block_size=65536):
    hash_alg = hash_algorithm()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(block_size):
                hash_alg.update(chunk)
        return file_path, hash_alg.hexdigest()
    except Exception as e:
        print(f"Could not read file {file_path}: {e}")
        return file_path, None

def hash_compare_method(directories):
    hash_dict = {}
    duplicates = []

    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_hash = calculate_hash(file_path)
                except Exception as e:
                    print(f"Could not read file {file_path}: {e}")
                    continue

                if file_hash in hash_dict:
                    duplicates.append(file_path)
                    print(f"Duplicate found: {file_path} is a duplicate of {hash_dict[file_hash]}")
                else:
                    hash_dict[file_hash] = file_path

    return hash_dict, duplicates

def multithreaded_compare_method(libraries, max_workers=4):
    hash_dict = {}
    duplicates = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for library in libraries:
            for book_file in library.book_files:
                futures.append(executor.submit(calculate_hash, book_file))

        for future in as_completed(futures):
            file_path, file_hash = future.result()
            if file_hash is None:
                continue

            if file_hash in hash_dict:
                duplicates.append(file_path)
                print(f"Duplicate found: {file_path} is a duplicate of {hash_dict[file_hash]}")
            else:
                hash_dict[file_hash] = file_path

    return hash_dict, duplicates


if __name__ == "__main__":
    if not root:
        sys.exit(0)

    book_files = []
    unique_files = []
    duplicate_files = []
    libraries_with_files = []
    libraries_save_file = WindowsPath(r"C:\MyProjects\Scripts\libraries_with_files.txt")
    compare_file = WindowsPath(r"C:\MyProjects\Scripts\compare_file.txt")
    save_unique_files_list = WindowsPath(r"C:\MyProjects\Scripts\book_list_file.txt")

    for l in root:
        library = Library(l)
        if not library.author_paths:
            # print(f"No authors in {library.path}")
            continue
        library.get_book_dirs()
        if not library.book_dirs:
            # print(f"No book directories in {library.path}")
            continue
        library.get_ebook_files()
        if library.book_files:
            print(f"Adding {library.path} to libraries_with_files")
            libraries_with_files.append(library)
    # if not libraries_with_files:
    try:
        print(f"{libraries_with_files = }")
    except:
        print(f"libraries_with_files is empty")
        sys.exit(0)
    

# single process hash compare
# directories_to_check = ["dir1", "dir2", "dir3", "dir4", "dir5", "dir6", "dir7", "dir8"]
# unique_files, duplicate_files = hash_compare_method(directories_to_check)

# multithreaded hash compare
unique_files, duplicate_files = multithreaded_compare_method(libraries_with_files)
print(f"Unique files: {len(unique_files)}")
print(f"Duplicate files: {len(duplicate_files)}")


