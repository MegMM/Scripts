from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import hashlib
from pathlib import Path, WindowsPath
import os
import pandas as pd
import re
from shutil import copy2

extensions = ['.doc', '.mobi', '.zip', '.docx', '.azw3', '.azw', '.pdf', '.epub', '.txt', '.rtf', '.lit', '.kfx', '.original_mobi', '.pdb', '.htm', '.html', '.kfx-zip', '.prc', '.pdr', '.cbz', '.md', '.htmlz', '.tan', '.azw4', '.aax', '.original_epub']

use_saved_files = False
unique_files = []
duplicates_files = []

root_directory = WindowsPath(r"C:\Users\megha\OneDrive\Calibre Libraries")
new_root_directory = WindowsPath(r"C:\Calibre Library\onedrive_unique_files")
output_root = WindowsPath(r"C:\MyProjects\Scripts\calibre_libraries_merge\output")
save_uniques_file = output_root/r"uniques_file.txt"
save_duplicates_file = output_root/r"duplicates_file.txt"
save_all_file = output_root/r"all_files.txt"

def get_subdirs_with_files(subx):
    for sx in subx.iterdir():
        if x.is_file() and x.suffix in extensions:
            
def get_directories_with_files(root):
    dirs = [x for x in root.iterdir() if x.is_dir()]
    with_files = get_subdirs_with_files(dirs)

def get_all_filepaths(root):
    file_list = []
    for x in root.iterdir():
        if x.parents[0] is root:
            next
        if x.is_file() and x.suffix in extensions:
            file_list.append(x)
        elif x.is_dir():
            # print(f"directory: {x.parents[0]}")
            file_list.extend(get_all_filepaths(x))
    # file_list.extend([x for x in x.iterdir() if x.is_file() and x.suffix in extensions] +\
    #                  [y for y in x.iterdir() if y.is_dir()])
    return file_list

def save_list_to_file(list_name: list, file_name: Path):
    with open(file_name, 'w') as f:
        for file_path in list_name:
            f.write(f"{file_path}\n")

def extract_metadata(file_list):
    file_data_list = []
    for wpl in file_list:
        file_data = {}
        wpp = wpl.parts[5:]
        # if (root_directory/wpp[0]).is_file():
        #     # print(f"{(root_directory/wpp[0]).is_file()}")
        #     next
        # else:
        file_data['id'] = re.sub(r"[\[\]\(\) '&*-.]", "", wpl.stem.lower())
        file_data['lib'] = wpp[0]
        file_data['author'] = wpp[1]
        file_data['path'] = str(wpl)
        file_data['name'] = wpl.stem
        file_data['format'] = wpl.suffix
        file_data['size'] = f"{os.path.getsize(wpl)/1024:.2f} Kb"
        file_data['created'] = datetime.fromtimestamp(os.path.getctime(wpl)).strftime('%Y-%m-%d %H:%M:%S')
        file_data['last_modified'] = datetime.fromtimestamp(os.path.getmtime(wpl)).strftime('%Y-%m-%d %H:%M:%S')
        file_data_list.append(file_data)
    return file_data_list
    
def compute_file_hash(file_path, hash_algorithm=hashlib.sha256):
    hasher = hash_algorithm()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest(), file_path

def get_unique_files_parallel(root_directory, all_files, extensions, max_workers=8):
    unique_files = {}
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



if __name__ == "__main__":
    # if use_saved_files:
    #     with open(save_uniques_file, 'r') as suf:
    #         unique_files = [line.rstrip() for line in suf]
    #     with open(save_duplicates_file, 'r') as sdf:
    #         duplicates_files = [line.rstrip() for line in sdf]

    # else:
    assert root_directory.is_dir()
    all_files = get_all_filepaths(root_directory)
    # print(all_files)
    save_list_to_file(all_files, save_all_file)
    # print(f"Running parallel hashing compare on {root_directory = }")
    # unique_files, duplicate_files = get_unique_files_parallel(root_directory, all_files, extensions)
    all_metadata = extract_metadata(all_files)
    columns = ['id', 'lib', 'author', 'path', 'name', 'size', 'created', 'last_modified']
    df = pd.DataFrame.from_dict(all_metadata)
    df.to_excel(output_root/r'output_all_libraries.xlsx')
