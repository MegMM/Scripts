from pathlib import WindowsPath
import pandas as pd

extensions = ['.doc', '.mobi', '.zip', '.docx', '.azw3', '.azw', '.pdf', '.epub', '.txt', '.rtf', '.lit', '.kfx', '.original_mobi', '.pdb', '.htm', '.html', '.kfx-zip', '.prc', '.pdr', '.cbz', '.md', '.htmlz', '.tan', '.azw4', '.aax', '.original_epub']

def get_extensions(file):
    if file.is_file():
        if file.suffix not in extensions:
            extensions.append(file.suffix)


path = WindowsPath(r"C:\Users\megha\OneDrive\Calibre Libraries")
main_libs = [p for p in path.iterdir() if p.is_dir()]
# print(main_libs)


class Library:
    def __init__(self, path):
        self.path = path
        self.name = self.path.stem
        try:
            self.authors = self.get_authors()
        except Exception as e:
            print(f"Error: {e}")
        # print(self.authors)
        try:
            self.get_books()
            print(self.books)
        except Exception as e:
            print(f"Error: {e}")
        # self.get_file_paths()

    def get_authors(self):
        # returns list of Paths
        return [a for a in self.path.iterdir() if a.is_dir()]

    def get_books(self):
        for a in self.authors:
            author = Author(a)
            self.books = author.get_books()
            
    def get_file_paths(self):
            self.book_files = author.get_book_files()


class Author:
    def __init__(self, name):
        self.name = name
        self.books = self.get_books()

    def get_books(self):
        return [book for book in self.name.iterdir() if book.is_dir()]

    def get_book_files(self):
        return [file for file in self.books.iterdir() if self.is_ebook(file)]

    def is_ebook(ebook):
        if ebook.suffix in extensions:
            return ebook

for l in main_libs:
    print(l)
    if l.is_dir():
        try:
            library = Library(l)
            print(f"\n{library.name = }")
            # print(f"\n\n Library Authors:")
            # print(f"{library.authors = }")
            print(f"Library Books:")
            print(f"{library.books = }")
        except Exception as e:
            print(f"Error: Library object: {e}")
    # print("\n")
    # # print(lib)
    # authors = [a for a in lib.iterdir() if a.is_dir()]
    # for author in authors:
    #     auth_books = [book for book in author.iterdir() if book.is_dir()]
    #     # print(auth_books)
    #     for book_dir in auth_books:
    #         # for file in book_dir.iterdir():
    #         book_files = [file for file in book_dir.iterdir() if is_ebook(file)]
    #         print(book_files)

# print(extensions)