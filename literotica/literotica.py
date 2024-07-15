from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import WindowsPath
import requests

liter_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"}
# def is_good_response(self, resp)  -> bool:
def is_good_response(resp)  -> bool:
    return (resp.status_code == 200)

def request_page(url, header):
    with requests.Session() as req:
        req.headers.update(header)
        resp = req.get(url)
        # print(resp.request.headers)
        try:
            if is_good_response(resp):
                print(f"URL request good.")
        except requests.exceptions.HTTPError as e:
            print(f"ERROR in page content: {str(e)}")
    return resp.text

def get_chapter_title(soup):
    pass

def get_full_page_urls(chapters):
    page_breadcrumbs = []
    for ch in chapters:
        ch_soup = BeautifulSoup(request_page(ch['chapter_url'], header), 'html.parser')
        pg_list = ch_soup.find_all('a', {'class': 'l_bJ'})
        chapter_title = get_chapter_title(ch_soup)
        page_breadcrumbs.extend([pg['href'] for pg in pg_list])
    return [f'{site_url}{pg}' for pg in page_breadcrumbs]

## tmp ## series_url = input("Enter story url base: ")
site_url = "https://www.literotica.com/"
series_url = r"https://www.literotica.com/series/se/14186"
# https://www.literotica.com/series/se/14186
# https://www.literotica.com/s/silver-1
# https://www.literotica.com/s/silver-1?page=2
# https://www.literotica.com/s/silver-ch-02
# page = request_page(series_url)
if 'liter' in series_url:
    header = liter_header
soup = BeautifulSoup(request_page(series_url, header), 'html.parser')
toc = soup.find('div', {'class': "aa_ht"}).find_all('li')
# toc = soup.div{'class': 'aa_ht'}.find_all('li')
chapters = [{'chapter_title': li.text, 'chapter_url': li.a['href']} for li in toc]
# print(chapters)
    
full_urls = get_full_page_urls(chapters)
print(full_urls)

for pg in full_urls:
    ch_soup = 





