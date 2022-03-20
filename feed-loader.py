import feedparser
from bs4 import BeautifulSoup  # 导入bs4库
import urllib.request
import sys
import os
import time
import sqlite3
import eventlet
import re


def log(str):
    print(str)

def replace(str):
  # apst for apostrophe '
  # _equ_ for =
  return str.replace('.', '_d').\
  replace(':', '_t')\
    .replace('/', '_b')\
      .replace('?','_d2')\
        .replace("'",'_a')\
        .replace('=','_e')\
          .replace('-','_s')\
          .replace('%','_0')
def parse_raw(feed, str):
    eventlet.monkey_patch()
    with eventlet.Timeout(5, False):
        try:
            return replace(feed[str])
        except:
            return 'null'


def get_title(feed):
    return parse_raw(feed, 'title')


def get_author(feed):
    return parse_raw(feed, 'author')


def get_contex_raw(feed):
    return parse_raw(feed, 'summary')


def get_key1(feed):
    return parse_raw(feed, 'key1')


def get_key2(feed):
    return parse_raw(feed, 'key2')


def get_key3(feed):
    return parse_raw(feed, 'key3')


def get_update_time(feed):
    return 'datetime(1092941466, \'unixepoch\', \'localtime\')'
def parse_url_data(url):
    data_list = []
    try:
        eventlet.monkey_patch()
        with eventlet.Timeout(60, False):
            feed_data = feedparser.parse(url)
        if len(feed_data) != 0:
            for feed_row in feed_data.entries:
                data_row = (feed_row.link, get_update_time(feed_row), \
                    get_title(feed_row), get_author(feed_row), get_contex_raw(feed_row), \
                    get_key1(feed_row), get_key2(feed_row), \
                    get_key3(feed_row))
                data_list.append(data_row)
    except:
        log('parse data failed')
    else:
        log('parse success')
    return data_list


def update_markdown(row, file):
    file.writelines('\n\n ['+row[2]+']('+row[0]+')')
    file.writelines('\n\n> 作者： ' + row[3] + '  更新时间： '+row[1])
    # if row[4] != 'null':
      # file.writelines('\n\n'+row[7])


def main():
    # prepare markdown files
    localtime = time.localtime(time.time())
    folder_name = str(localtime.tm_year) + '-' + str(localtime.tm_mon)
    folder = os.path.exists(folder_name)
    if not folder:
        os.makedirs(folder_name)
    file_name = folder_name + '/'+str(localtime.tm_mday)+".md"
    is_exists = os.path.exists(file_name)
    file = open(file_name, "a")
    if not is_exists:
        file.write("\n## "+str(localtime.tm_year)+"-" +
                   str(localtime.tm_mon)+"-"+str(localtime.tm_mday))
    # upate markdown files
    url_list = open('list.txt', 'r').read().splitlines()
    for url in url_list:
        data_list = parse_url_data(url)
        for data in data_list:
            update_markdown(data, file)

    file.writelines('\n')
    file.close()
    if not is_exists:
        history = 'history'
        if not os.path.exists(history):
            os.makedirs(history)
        file_list = history + '/file_list.md'
        readme = open(history + "/file_list.md", "a")
        readme.writelines("\n\n["+str(localtime.tm_year)+"-"+str(
            localtime.tm_mon)+"-"+str(localtime.tm_mday)+"]("+file_name+")")
        readme.close()


if __name__ == "__main__":
    main()
