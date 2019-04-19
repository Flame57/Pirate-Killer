import csv
import requests
import urllib
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from wxpy import *


def do_request(url_in):
    # 请求网页

    def get_fake_header():
        ua = UserAgent()
        fake_headers = {'User-Agent': ua.random}
        return fake_headers

    headers = get_fake_header()
    try:
        wb_data = requests.get(url_in, headers=headers)
        html_sp_out = BeautifulSoup(wb_data.text, 'lxml')
    except requests.RequestException as request_err:
        print('\n', '=' * 50, "\nrequest error:\n", request_err)
        html_sp_out = None

    return html_sp_out


def do_xianyu(xianyu_word):

    url_0 = 'https://s.2.taobao.com/list/?q='
    url_key_word = urllib.parse.quote(xianyu_word, encoding='gbk')
    url_99 = '&search_type=item&app=shopsearch'
    url_full = url_0 + url_key_word + url_99

    html_soup = do_request(url_full)

    items = html_soup.select("div.item-pic > a")
    sellers = html_soup.select("div.seller-avatar > a")
    attention_list_out = [{
        'title': iItem.get('title'),
        'seller': iSeller.get('title'),
        'link': 'https:' + iItem.get('href')
    } for iItem, iSeller in zip(items, sellers)]

    print(f'搜索闲鱼 关键词: {xianyu_word}  -  完成')
    return attention_list_out


def save_xianyu_info(data_list, filepath_write='./xianyu_info.txt'):

    with open(filepath_write, "w", encoding='utf8', newline='') as xianyu_file:
        file_header = ['title', 'seller', 'link']
        csv_dict_writer = csv.DictWriter(xianyu_file, file_header)
        csv_dict_writer.writeheader()
        csv_dict_writer.writerows(data_list)
        xianyu_file.close()

    return 0


def send_wechat_notice(wechat_user, filepath_send):

    wechat_user.send_file(filepath_send)

    return 0






