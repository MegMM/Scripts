import os
from pathlib import WindowsPath, Path

extensions = ['.doc', '.mobi', '.zip', '.docx', '.azw3', '.azw', '.pdf', '.epub', '.txt', '.rtf', '.lit', '.kfx', '.original_mobi', '.pdb', '.htm', '.html', '.kfx-zip', '.prc', '.pdr', '.cbz', '.md', '.htmlz', '.tan', '.azw4', '.aax', '.original_epub']

use_saved_files = False
unique_files = []
duplicates_files = []

root_directory = WindowsPath(r"C:\Users\megha\OneDrive\Calibre Libraries")
new_root_directory = WindowsPath(r"C:\Calibre Library\onedrive_unique_files")
save_uniques_file = WindowsPath(r"C:\MyProjects\Scripts\uniques_file.txt")
save_duplicates_file = WindowsPath(r"C:\MyProjects\Scripts\duplicates_file.txt")

if use_saved_files:
    with open(save_uniques_file, 'r') as suf:
        unique_files = [line.rstrip() for line in suf]
    with open(save_duplicates_file, 'r') as sdf:
        duplicates_files = [line.rstrip() for line in sdf]

else:
    

