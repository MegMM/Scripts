import os
import hashlib
from pathlib import Path
import pickle

class Library:
    def __init__(self, path, extensions):
        if path and isinstance(path, Path):
            self.path = path
            self.name = self.path.stem
            self.author_paths = []
            self.book_files = []
            self.book_dirs = []
            self.extensions = extensions
            self.get_author_paths()
            self.get_book_dirs()
            self.get_ebook_files()

    def get_author_paths(self):
        self.author_paths = [a for a in self.path.iterdir() if a.is_dir() and 'calnote' not in a.stem]

    def get_book_dirs(self):
        self.book_dirs = [b for p in self.author_paths for b in p.iterdir() if b.is_dir()]

    def get_ebook_files(self):
        for dir in self.book_dirs:
            if dir.is_dir():
                files = [f for f in dir.iterdir() if f.suffix in self.extensions]
                self.book_files.extend(files)

    def compute_file_hash(self, file_path, hash_algorithm=hashlib.sha256):
        hasher = hash_algorithm()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def get_unique_files(self):
        unique_files = {}
        for file in self.book_files:
            file_hash = self.compute_file_hash(file)
            if file_hash not in unique_files:
                unique_files[file_hash] = file
        return list(unique_files.values())

    @staticmethod
    def contains_files_with_extensions(directory, extensions):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if Path(file).suffix in extensions:
                    return True
        return False

# Function to scan root directory and create Library objects
def create_libraries(root_directory, extensions):
    libraries = []
    for subdir in root_directory.iterdir():
        if subdir.is_dir() and Library.contains_files_with_extensions(subdir, extensions):
            libraries.append(Library(subdir, extensions))
    return libraries

def save_list_to_file(items_list, save_file):
    with open(save_file, 'wb') as f:
        pickle.dump(items_list, f)

def get_list_from_file(save_file):
    with open (save_file, 'rb') as fp:
        return pickle.load(fp)

def save_unique_files(libraries, save_unique_files_list):
    with open(save_unique_files_list, 'w') as f:
        for library in libraries:
            unique_files = library.get_unique_files()
            f.write(f"Library: {library.name}\n")
            for unique_file in unique_files:
                f.write(f"{unique_file}\n")
            f.write("\n")
    
if __name__ == "__main__":

    root_directory = WindowsPath(r"C:\Users\megha\OneDrive\Calibre Libraries")
    save_unique_files_list = WindowsPath(r"C:\MyProjects\Scripts\book_list_file.txt")
    duplicate_files = WindowsPath(r"C:\MyProjects\Scripts\duplicates.txt")
    
    extensions = ['.doc', '.mobi', '.zip', '.docx', '.azw3', '.azw', '.pdf', '.epub', '.txt', '.rtf', '.lit', '.kfx', '.original_mobi', '.pdb', '.htm', '.html', '.kfx-zip', '.prc', '.pdr', '.cbz', '.md', '.htmlz', '.tan', '.azw4', '.aax', '.original_epub']
    
    libraries = create_libraries(root_directory, extensions)
    save_unique_files(libraries, save_unique_files_list)
    
    # for library in libraries:
    #     unique_files = library.get_unique_files()
    #     with open(save_unique_files_list, 'w+') as f:
    #         f.write(f"Library: {library.name}")
    #         for unique_file in unique_files:
    #             f.writelines(unique_file)
