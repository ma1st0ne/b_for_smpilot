from bs4 import BeautifulSoup
import requests


def get_proxy():
    HIDEMY_URL = 'https://hidemy.name/ru/proxy-list/?country=DE&ports=80'
    headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0'}
    r = requests.get(HIDEMY_URL, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find(class_='table_block')
    tr_list = table.tbody.find_all('tr')
    ips = []
    for tr in tr_list:
        td = tr.find_all('td')
        ips.append(td[0].text)
    return ips
