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
def open_table(path, url):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    table = replace(url)
    print(table)
    lookup_table = "select count(*)  from sqlite_master where type='table' and name = " + \
        '\''+table+'\''
    print(lookup_table)
    res = cur.execute(lookup_table).fetchall()
    print(res)
    if not res[0][0]:
        create_table = "create table " + table \
            + "(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
            URL TEXT NOT NULL, \
            UPDATE_TIME TIMESTAMP,\
            FETCH_TIME DATETIME DEFAULT (datetime('now','localtime')),\
            TITLE TEXT, \
            AUTHOR TEXT,\
            CONTENT TEXT, \
            CONTEXT_RAW TEXT, \
            KEY_WORDS1 TEXT,\
            KEY_WORD2 TEXT, \
            KEY_WORD3 TEXT, \
            REFERENCE NUMBERS NOT NULL);"
        res = cur.execute(create_table)
        conn.commit()
        if len(res.fetchall()) == 0:
            print('table create: ' + table)
    return (cur, table, conn)


def insert_table(cur, table, conn, url):
    url_data = parse_url_data(url)
    insert_rows(cur, table, conn, url_data)


def insert_rows(cur, table, conn, url_data):
    for url_row in url_data:
        lookup_table = "select * from " + table + " where URL = " + '"' + url_row[0] + '"'
        res = cur.execute(lookup_table)
        if len(res.fetchall()) == 0:
            insert_table = "insert into " + table + \
                " (URL, UPDATE_TIME, TITLE, AUTHOR, CONTENT, CONTEXT_RAW, KEY_WORDS1, KEY_WORD2, KEY_WORD3, REFERENCE) values " + \
                url_row[1]
            # print(insert_table)
            cur.execute(insert_table)
    conn.commit()


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
        with eventlet.Timeout(50, False):
            feed_data = feedparser.parse(url)
        if len(feed_data) != 0:
            for feed_row in feed_data.entries:
                data_row = '(\''+feed_row.link+'\','+get_update_time(feed_row)+',\'' \
                    + get_title(feed_row)+'\',\''+get_author(feed_row)+'\',null,\''+get_contex_raw(feed_row) \
                    + '\',\'' + \
                    get_key1(feed_row)+'\',\''+get_key2(feed_row) + \
                    '\',\''+get_key3(feed_row)+'\',1)'
                data_list.append([feed_row.link, data_row])
    except:
        log('parse data failed')
    else:
        log('parse success')
    return data_list


def update_markdown(row, file):
    file.writelines('\n\n ['+row[4]+']('+row[1]+')')
    file.writelines('\n\n> 作者： ' + row[5] + '  拉取时间： '+row[3])
    # if row[7] != 'null':
      # file.writelines('\n\n'+row[7])


def main():
    # update sqlite3
    url_list = open('list.txt', 'r').read().splitlines()
    for url in url_list:
        cur, table, conn = open_table('.database/feed-2022-03.sqlit3', url)
        insert_table(cur, table, conn, url)
    # prepare markdown files
    localtime = time.localtime(time.time())
    file_name = str(localtime.tm_year)+"/" + \
        str(localtime.tm_mon)+'-'+str(localtime.tm_mday)+".md"
    is_exists = os.path.exists(file_name)
    file = open(file_name, "a")
    if not is_exists:
        file.write("\n## "+str(localtime.tm_year)+"-" +
                   str(localtime.tm_mon)+"-"+str(localtime.tm_mday))
    # upate markdown files
    fetch_table = "select name from sqlite_master where type=\'table\' and name != \'sqlite_sequence\'"
    table_list = cur.execute(fetch_table).fetchall()
    for table_one in table_list:
        fetch_updated_data = 'select * from ' + \
            table_one[0] + \
            ' where fetch_time >= date(\'now\', \'-1 day\') order by fetch_time desc'
        # print(fetch_updated_data)
        today_data = cur.execute(fetch_updated_data).fetchall()
        for row in today_data:
            # print(row)
            update_markdown(row, file)
    file.writelines('\n')
    file.close()
    if not is_exists:
        readme = open("ARCHIVED.md", "a")
        readme.writelines("\n\n["+str(localtime.tm_year)+"-"+str(
            localtime.tm_mon)+"-"+str(localtime.tm_mday)+"]("+file_name+")")
        readme.close()


if __name__ == "__main__":
    main()
