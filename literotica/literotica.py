
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime
from pathlib import WindowsPath, Path
import pickle
import requests

    ## tmp ## series_url = input("Enter story url base: ")
    # https://www.literotica.com/series/se/14186
    # https://www.literotica.com/s/silver-1
    # https://www.literotica.com/s/silver-1?page=2
    # https://www.literotica.com/s/silver-ch-02
    
site_url = "https://www.literotica.com/"
series_url = r"https://www.literotica.com/series/se/14186"
liter_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"}


def is_good_response(resp)  -> bool:
    return (resp.status_code == 200)

def request_page(url, header):
    with requests.Session() as req:
        req.headers.update(header)
        resp = req.get(url)
        try:
            if is_good_response(resp):
                # too much output
                # print("Page request good")
                pass
        except requests.exceptions.HTTPError as e:
            print(f"ERROR in page content: {str(e)}")
    return resp.text


class FileHandler:
    def __init__(self, story_title, author=None):
        self.root = WindowsPath(WindowsPath(__file__).parent)
        self.story_title = story_title.lower()
        print(f"FileHandler: {self.story_title = }")
        self.story_dir = self.root/self.story_title
        # print(self.story_dir)
        self.story_dir.mkdir(exist_ok=True)
        # compiled story pages
        self.story_file = self.story_dir/f"{story_title}.html"
        # soup files
        self.soup_dir = self.root/fr"soup\{story_title}"
        self.soup_dir.mkdir(exist_ok=True, parents=True)
        # file check
        self.has_soup_files = [f.is_file() for f in self.soup_dir.iterdir()]
        # toc file name
        self.toc_from_web = self.story_dir/"toc.html"

    def save_chapter_page(self, page):
        # save chapter pages to chapter directory
        chapter_dir = self.root/f'chapter_{page.ch_num}'
        chapter_dir.mkdir(exist_ok=True)
        file_name = chapter_dir/f"{page['file_name']}.html"
        with open(file_name, mode='w+', encoding='utf-8') as pf:
            for tag in page['content']:
                pf.write(str(tag))

    def save_soup_page(self, soup, filename):
        # filename is formatted "chapter_num_page_num.html" all in single directory
        with open(self.soup_dir/filename, 'w+', encoding='utf-8') as fn:
            fn.write(soup.prettify())

 
class DownloadHandler(FileHandler):
    def __init__(self, story_title, author=None):
        super().__init__(story_title, author)  # Corrected this line
        self.story_title = story_title.lower()
        self.save_soup = False
        print(f"DownloadHandler: {self.story_title = }")
        if 'liter' in series_url:
                self.header = liter_header

    def gather_story_files(self, series_url, source="from_files", save_soup=False):
        force_download = "from_web" in source
        self.save_soup = save_soup
        if "from_web" in source or "from_files" in source:
            pass
        else:
            print('Options are "from_web" or "from_files"')
            return
        # print(f"{self.toc_from_web.is_file() = }, {bool(self.has_soup_files) = }, {force_download = }")
        if bool(self.has_soup_files) and not force_download:
            print('Collecting local HTML files...')
            self.toc_from_files = [f for f in self.soup_dir.iterdir()]
            print(f"gather_story_files: {self.save_soup = }")
            self.collect_chapters_from_files()
            # print(self.toc_from_files)

        elif not self.has_soup_files or force_download:
            print("Downloading TOC from web...")
            self.save_soup = True
            self.soup = BeautifulSoup(request_page(series_url, self.header), 'html.parser')
            self.save_soup_page(self.soup, "toc.html")
            self.toc_from_web = self.soup.find('div', {'class': "aa_ht"}).find_all('li')
            self.collect_chapters_from_web()

    def collect_chapters_from_web(self):
        print(f"Collecting story pages for {self.story_title} by {self.author}")
        chapter_starts = []
        for i, li in enumerate(self.toc_from_web):
            chapter_starts.append({'chapter_num': i, 'chapter_url': li.a['href']})
        self.chapters = [Chapter(pg, self.story_title, self.save_soup) for pg in chapter_starts]

    def collect_chapters_from_files(self):
        chapters = []
        for file in self.toc_from_files:
            if 'toc' in file.name:
                continue
            found = False
            ch_num = int(file.name.split('chapter')[1].split("_")[0])
            for chapter in chapters:
                if chapter['chapter_num'] == ch_num:
                    found = True
                    if file not in chapter['pages']:
                        chapter['pages'].append(file)
                        # chapter['pages'].append(file.as_uri())
                    break
            if not found:
                # chapters.append({'chapter_num': ch_num, 'pages': [file.as_uri()]})
                chapters.append({'chapter_num': ch_num, 'pages': [file]})
        # print(chapters[0]['pages'][0])
        with open(chapters[0]['pages'][0], encoding='utf-8') as rf:
            self.soup = BeautifulSoup(rf.read(), 'html.parser')
        # self.chapters = [Chapter(pg) for pg in chapters]
        for pg in chapters:
            print(f"collect_chapters_from_files: {self.save_soup = }")
            print(f"collect_chapters_from_files: chapters {pg = }")
            ch = Chapter(pg, self.story_title, self.save_soup)
            print(f"{ch = }")

    def title_author_html(self):
        print( self.soup.find('a', {'class': 'y_eU'}))
        self.author = self.soup.find('a', {'class': 'y_eU'}).text
        self.story_title = "Adventures of the Crew of the Spaceship Silver"
        return f"""
<div>
  <h2>{self.story_title}</h2>
  <p> </>
  <h3>by<h3
  <p> </>
  <h2>{self.author}</h2>
</div>
                """

    def write_story(self):
        title_html = self.title_author_html()
        with open(self.story_file, 'w+', encoding='utf-8') as fn:
            fn.write(title_html)
            for ch in self.chapters:
                fn.write("<div><p> </p></div>")
                fn.write("<div>")
                fn.write(ch.content.prettify())
                fn.write("</div>")
                


class Chapter(DownloadHandler):
    def __init__(self, pg, story_title, save_soup):
        super().__init__(story_title)
        # print(f"Chapter: {self.story_title = }")
        self.save_soup = save_soup
        print(f"Chapter: {self.save_soup = }")
        if self.save_soup:
            self.first_page = pg['chapter_url']
            self.ch_num = pg['chapter_num']+1
            print(f"Collecting Chapter {self.ch_num}")
            self.get_from_webpage()
        else:
            print(f"Chapter: {pg =}")
            self.first_page = pg['chapter_url']
            self.get_from_local_file()
            
    def get_from_webpage(self):
            self.start_soup = BeautifulSoup(request_page(self.first_page, self.header), 'html.parser')
            self.pg_list = self.start_soup.find('div', {'class': 'panel clearfix l_bH'}).find_all('a', {'class': 'l_bJ'})
            self.href_snippets = [a['href'] for a in self.pg_list if 'href' in a.attrs]
            self.content = []
            self.get_ch_content()
            
    def get_from_local_file(self):
        with open(pg, encoding="utf-8") as rf:
            self.start_soup = BeautifulSoup(rf.read(), 'html.parser')
        print()
        self.href_snippets = [a['href'] for a in self.pg_list if 'href' in a.attrs]
        self.content = []
        self.get_ch_content()

    def get_ch_content(self):
        # saving all files to single directory for soup and for extracts
        for i, snippet in enumerate(self.href_snippets):
            if self.save_soup:
                formatted_url = f"{site_url}{snippet}"
                self.soup = BeautifulSoup(request_page(formatted_url, self.header), 'html.parser')
            else:
                with open(self.chapters[0]['pages'][0], encoding='utf-8') as rf:
                    self.soup = BeautifulSoup(rf.read(), 'html.parser')
            ptags = ptags_from_soup = self.soup.find('div', {'class': "aa_ht"}).find('div').find_all('p')
            self.content.extend(ptags)
            # filename = f'page_{i+1}.html'
            filename = f'chapter{self.ch_num}_page{i+1}.html'
            self.save_chapter_page({'file_name': filename, 'content': ptags})
            if self.save_soup:
                # self.save_soup_page(soup, f"chapter{self.ch_num}_{filename}.html")
                self.save_soup_page(self.soup, filename)

    def save_chapter_page(self, page):
        chapter_dir = WindowsPath(__file__).parent/f'chapter_{self.ch_num}'
        chapter_dir.mkdir(exist_ok=True)
        file_name = chapter_dir/f"{page['file_name']}"
        with open(file_name, mode='w+', encoding='utf-8') as pf:
            for tag in page['content']:
                pf.write(str(tag))


if __name__ == "__main__":
    # story_title = input("Enter Story title: ")
    # author = input("Enter Author: ")
    # story_title = dh.soup.title.text.split(' -')[0]
    story_name = "Silver"
    author = "Pelaam"
    dh = DownloadHandler(story_name, author)
    dh.gather_story_files(series_url, source="from_files", save_soup=False)
    dh.write_story()

