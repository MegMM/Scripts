from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import WindowsPath
import requests


site_url = "https://www.literotica.com/"
series_url = r"https://www.literotica.com/series/se/14186"
liter_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"}
# def is_good_response(self, resp)  -> bool:
outfile = WindowsPath(r".\outfile.html")
def is_good_response(resp)  -> bool:
    return (resp.status_code == 200)

def request_page(url, header):
    with requests.Session() as req:
        req.headers.update(header)
        resp = req.get(url)
        try:
            if is_good_response(resp):
                pass
        except requests.exceptions.HTTPError as e:
            print(f"ERROR in page content: {str(e)}")
    return resp.text

class Chapter:
    def __init__(self, header, pg):
        ch_url = pg['chapter_url']
        self.start_soup = BeautifulSoup(request_page(ch_url, header), 'html.parser')
        self.pg_list = self.start_soup.find('div', {'class': 'panel clearfix l_bH'}).find_all('a', {'class': 'l_bJ'})
        self.href_snippets = [a['href'] for a in self.pg_list if 'href' in a.attrs]
        print(f"{len(self.href_snippets) = }")
        self.content = [self.start_soup.find('div', {'class': "aa_ht"}).find_all('p')]
        # print(f"{(self.content[0]) = }")
        self.get_ch_content()

    def get_ch_content(self):
        for snippet in self.href_snippets[1:]:
            formatted_url = f"{site_url}{snippet}"
            print(f"{formatted_url = }")
            soup = BeautifulSoup(request_page(formatted_url, header), 'html.parser')
            ptags = soup.find('div', {'class': "aa_ht"}).find('div').find_all('p')
            # print(len(ptags))
            # print(f"{ptags}")
            self.content.extend(ptags)
        # print(f"{self.content}")


if __name__ == "__main__":
    ## tmp ## series_url = input("Enter story url base: ")
    # https://www.literotica.com/series/se/14186
    # https://www.literotica.com/s/silver-1
    # https://www.literotica.com/s/silver-1?page=2
    # https://www.literotica.com/s/silver-ch-02
    # page = request_page(series_url)
    if 'liter' in series_url:
        header = liter_header

    print("Collecting TOC...")
    soup = BeautifulSoup(request_page(series_url, header), 'html.parser')
    toc = soup.find('div', {'class': "aa_ht"}).find_all('li')
    first_page_urls = [{'chapter_title': li.text, 'chapter_url': li.a['href']} for li in toc]
    print("Collecting story pages...")
    # chapter = Chapter(header, first_page_urls[0])
    # chapters = [Chapter(header, pg) for pg in first_page_urls]
    chapters = []
    for pg in first_page_urls:
        Chapter(header, pg)
        chapters.append(pg)
        
    # print(len(chapters))
    # with open(outfile, 'w+', encoding='utf-8') as ofi:
    #     for ch in chapters:
    #         ofi.write(str(ch.title))
    #         for tag_list in ch.content:
    #             [ofi.write(str(tag)) for tag in tag_list]
    #             ofi.write(f'\n***\n')

