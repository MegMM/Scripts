
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime
from pathlib import WindowsPath, Path
import pickle
import re
import requests

    ## tmp ## series_url = input("Enter story url base: ")
    # https://www.literotica.com/series/se/14186
    # https://www.literotica.com/s/silver-1
    # https://www.literotica.com/s/silver-1?page=2
    # https://www.literotica.com/s/silver-ch-02
    
site_url = "https://www.literotica.com/"
series_url = r"https://www.literotica.com/series/se/14186"
liter_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"}



class FileHandler:
    def __init__(self, story_dirname, author=None):
        self.root = WindowsPath(WindowsPath(__file__).parent)
        self.story_dirname = story_dirname
        self.story_dir = self.root/self.story_dirname
        self.soup_dir = self.root/fr"soup\{self.story_dirname}"
        self.story_file = self.story_dir/f"{self.story_dirname}.html"
        self.story_dir.mkdir(exist_ok=True)
        self.soup_dir.mkdir(exist_ok=True, parents=True)
        self.has_story_file = self.story_file.is_file()
        self.has_soup_files = bool([f.is_file() for f in self.soup_dir.iterdir()])

    def request_page(self, url, header) -> str:
        """
        _summary_: Request a an web url
        Args:
            url (str): site_url, series_url, page_url
            header (str): Minimum header needed to make Request
        Returns:
            str: Request text
        """
        def is_good_response(resp)  -> bool:
            return (resp.status_code == 200)
        
        with requests.Session() as req:
            req.headers.update(header)
            resp = req.get(url)
            try:
                if is_good_response(resp):
                    # print("Page request good") # too much output
                    pass
            except requests.exceptions.HTTPError as e:
                print(f"ERROR in page content: {str(e)}")
        return resp.text

    def save_chapter_page(self, page:dict) -> None: 
        """
        Description: Write a chapter page that contains only <p> tags
        Args: page (dict): Contains 'chapter_dir', 'filename', 'content'
        """
        filename = self.story_dir/page['chapter_dir']/f"{page['filename']}.html"
        with open(filename, mode='w+', encoding='utf-8') as fn:
            for tag in page['content']:
                fn.write(str(tag))

    def save_soup_page(self, soup, filename:str) -> None:
        """
        Description: Write soup file to a single central directory (per story)
        Args: 
            soup: BeautifulSoup soup
            filename: Use format "chapter#_page#.html"
        """
        with open(self.soup_dir/filename, 'w+', encoding='utf-8') as fn:
            fn.write(soup.prettify())

 
class Story(FileHandler):
    def __init__(self, story_dirname, story_name, author=None):
        """
        Description: Initialize Story class based on FileHandler()
        Args:
            story_dirname (str): Story title, needs to modified for directory usage
            author (str, None):  Defaults to None.
        """
        super().__init__(story_dirname=story_dirname, author=author)  # Corrected this line
        self.story_dirname = story_dirname
        self.story_name = story_name
        self.author = author
        self.save_soup = False
        # print(f"Story: {self.story_dirname = }")
        if 'liter' in series_url:
                self.header = liter_header

    def gather_story_files(self, series_url, source="from_files", save_soup=False):
        # save_soup = True # tmp
        from_web = source in "from_web"
        from_files = source in "from_files"
        force_download = from_web or save_soup
        self.save_soup = save_soup
        if (not from_web or from_files) or (from_web and from_files):
            print('Options are either "from_web" or "from_files"')
            return
        if self.has_soup_files and not force_download:
            print('Collecting local HTML files...')
            self.page_list = [f for f in self.soup_dir.iterdir()]
            # print(f"gather_story_files: {self.save_soup = }")
            self.collect_chapters_from_files()
        elif not self.has_soup_files or force_download:
            print("Downloading TOC from web...")
            self.copy_toc_from_web()
            # self.save_soup = True
            self.toc_from_web = self.soup_dir/"toc.html"
            self.soup = BeautifulSoup(self.request_page(series_url, self.header), 'html.parser')
            self.save_soup_page(self.soup, self.toc_from_web)
            self.collect_chapters_from_web()
         
    def collect_chapters_from_web(self):
        print(f"Collecting story pages for {self.story_name} by {self.author}")
        self.chapter_list = self.soup.find('div', {'class': "aa_ht"}).find_all('li')
        chapter_starts = [{'ch_num': i, 'ch_url': li.a['href']} \
                          for i, li in enumerate(self.chapter_list)]
        self.chapters = [Chapter(pg, self.story_dirname, self.save_soup) for pg in chapter_starts]

    def collect_chapters_from_files(self):
        def extract_ch_number(filename):
            match = re.search(r"chapter(\d+)_", filename)
            if match:
                return int(match.group(1))
            return None
        
        # sort chapters
        self.chapters_dict = {}
        for file in self.page_list:
            found = False
            ch_num = int(extract_ch_number(file.name))
            if ch_num is not None:
                if ch_num not in self.chapters_dict:
                    self.chapters_dict[ch_num] = {'pages': [file]}
                else:
                    self.chapters_dict[ch_num]['pages'].append(file)
        for ch_dict in self.chapters_dict:
            ch = Chapter(ch_dict, self.story_dirname)
            print(f"{ch = }")

    def title_author_html(self):
        print(self.soup.find('a', {'class': 'y_eU'}))
        self.author = self.soup.find('a', {'class': 'y_eU'}).text
        self.story_dirname = "Adventures of the Crew of the Spaceship Silver"
        return f"""
<div>
  <h2>{self.story_name}</h2>
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
                


class Chapter(Story):
    def __init__(self, first_pg: dict, story_dirname: str, save_soup: bool=False):
        # def __init__(self, story_dirname, story_name, author=None):
        super().__init__(story_dirname, None, None)
        self.save_soup = save_soup
        # self.save_soup = True # test
        if self.save_soup and hasattr('ch_url', first_pg):
            self.ch_pages = self.get_web_urls(first_pg['ch_url'])
            self.ch_num = first_pg['ch_num']+1
            print(f"Collecting Chapter {self.ch_num}")
            self.get_content_from_web()
        else:
            self.ch_pages = first_pg['pages']
            self.ch_num = first_pg['ch_num'] # no +1
            self.get_content_from_files()
        self.chapter_dir = self.root/f'chapter_{self.ch_num}'
         # chapter_dir = self.root/f'chapter_{page.ch_num}'
        self.chapter_dir.mkdir(exist_ok=True)
        self.content = []

    def get_web_urls(self, start_url):
        soup = BeautifulSoup(self.request_page(start_url, self.header), 'html.parser')
        div = soup.find('div', {'class': 'panel clearfix l_bH'})
        a_tags = div.find_all('a', {'class': 'l_bJ'})
        href_snippets = [a['href'] for a in a_tags if 'href' in a.attrs]
        # list of full urls
        self.ch_pages = [f"{site_url}{snippet}" for snippet in href_snippets]

    def get_content_from_web(self):
        for i, url in enumerate(self.ch_pages):
            soup = BeautifulSoup(self.request_page(url, self.header), 'html.parser')
            ptags = soup.find('div', {'class': "aa_ht"}).find('div').find_all('p')
            self.content.extend(ptags)
            # filename = f'page_{i+1}.html'
            filename = f'chapter{self.ch_num}_page{i+1}.html'
            page = {'chapter_dir':self.chapter_dir,
                    'filename': filename,
                    'content': ptags}
            self.save_chapter_page(page)
            if self.save_soup:
                self.save_soup_page(soup, filename)
        
        def get_content_from_files(self):
            pass


    # def get_web_urls(start_url):
    #     self.start_soup = BeautifulSoup(self.request_page(self.first_page, self.header), 'html.parser')
    #     self.page_hrefs = self.start_soup.find('div', {'class': 'panel clearfix l_bH'}).find_all('a', {'class': 'l_bJ'})
    #     self.snippets = [a['href'] for a in self.page_hrefs if 'href' in a.attrs]
    #     self.ch_pages = [f"{site_url}{snippet}" for snippet in self.snippets]
    #     print(self.ch_pages)
        
    # def get_pages_from_web(self):
    #         self.get_content_from_web()

    # def get_pages_from_files(self):
    #     for p in self.ch_pages:
    #         with open(p, encoding="utf-8") as rf:
    #             soup = BeautifulSoup(rf.read(), 'html.parser')
    #     ptags = soup.find('div', {'class': "aa_ht"}).find('div').find_all('p')
    #     self.content.extend(ptags)
    #     filename = f'chapter{self.ch_num}_page{i+1}.html'
    #     self.save_chapter_page({'file_name': filename, 'content': ptags})


    # def get_content_from_web(self):
    #     # saving all files to single directory for soup and for extracts
    #     for i, url in enumerate(self.ch_pages):
    #         soup = BeautifulSoup(self.request_page(url, self.header), 'html.parser')
    #         ptags = soup.find('div', {'class': "aa_ht"}).find('div').find_all('p')
    #         self.content.extend(ptags)
    #         # filename = f'page_{i+1}.html'
    #         filename = f'chapter{self.ch_num}_page{i+1}.html'
    #         self.save_chapter_page({'file_name': filename, 'content': ptags})
    #         if self.save_soup:
    #             self.save_soup_page(soup, filename)

    # def save_chapter_page(self, page):
    #     file_name = self.chapter_dir/f"{page['file_name']}"
    #     with open(file_name, mode='w+', encoding='utf-8') as pf:
    #         for tag in page['content']:
    #             pf.write(str(tag))


if __name__ == "__main__":
    # story_dirname = input("Enter Story title: ")
    # author = input("Enter Author: ")
    # story_dirname = dh.soup.title.text.split(' -')[0]
    story_dirname = "Silver"
    story_name = "Adventures of the Crew of the Spaceship Silver"
    author = "Pelaam"
    dh = Story(story_dirname, story_name, author)
    dh.gather_story_files(series_url, source="from_files", save_soup=False)
    # dh.write_story()

