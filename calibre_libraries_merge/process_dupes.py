import os
from pathlib import Path, WindowsPath
from datetime import datetime
import difflib
from operator import itemgetter
import pandas as pd
import re
import xlsxwriter


def similar_name(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()
# Example usage
# print(similar_name("Apple", "Appel"))  # Output: 0.8
# print(similar_name("Apple", "Mango"))  # Output: 0.0


def setup_file_data_list(file_list):
    file_data_list = []
    for line in file_list:
        file_data = {}
        wpl = WindowsPath(line)
        # print(f"{wpl =}")
        wpp = wpl.parts[5:]
        file_data['id'] = re.sub(r"[\[\]\(\) '&*-.]", "", wpl.stem.lower())
        file_data['lib'] = wpp[0]
        file_data['author'] = wpp[1]
        file_data['path'] = str(wpl)
        file_data['name'] = wpl.stem
        file_data['format'] = wpl.suffix
        file_data['size'] = f"{os.path.getsize(wpl)/1024:.2f} Kb"
        file_data['created'] = datetime.fromtimestamp(os.path.getctime(wpl)).strftime('%Y-%m-%d %H:%M:%S')
        file_data['last_modified'] = datetime.fromtimestamp(os.path.getmtime(wpl)).strftime('%Y-%m-%d %H:%M:%S')
        
        # print(f"{file_data = }")
        file_data_list.append(file_data)
    # print(file_data_list)
    return file_data_list

if __name__ == "__main__":
    save_duplicates_file = WindowsPath(r"C:\MyProjects\Scripts\duplicates_file.txt")
    with open(save_duplicates_file, 'r') as sdf:
        file_list = [line.rstrip() for line in sdf]

    file_data_list = setup_file_data_list(file_list)
    # print(author_list)
    columns = ['id', 'lib', 'author', 'path', 'name', 'size', 'created', 'last_modified']
    df = pd.DataFrame.from_dict(file_data_list)
    df.to_excel('output.xlsx')
    # for index, row in df.iterrows():
    #     print(f"{row['name']}, {row['size']}, {row['last_modified']}")
    # duplicates = df[df.duplicated]['name']
    # for data in duplicates:
    #     print(data)
        # print()  
        # Add an empty line for readability
    # grouped = df.groupby(['author'])
    # for author, group_data in grouped:
    #     print(f"Author: {author}")
    #     print(group_data)
    #     print()  # Add an empty line for readability