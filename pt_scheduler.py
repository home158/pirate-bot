from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from pprint import pprint
from datetime import datetime
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from telegram import Message 

import pt_config
import pt_db
import pt_bot
import time
import json
import random
import os
import requests
from bs4 import BeautifulSoup
import re
def current_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time

def ptt_crawler(board):
    channel_id = {
        "Baseball"      :   "-1002039062910",
        "NBA"           :   "-1001990819892",
        "Gossiping"     :   "-1001782918396",
        "Lifeismoney"   :   "-1001543097185",
        "give"          :   "-1001776577088",
        "Test"          :   "-1001724672190",
        "Broad_Band"    :   "-1001615826339"
    }
    deny = "公告|協尋"
    allow = {
        "Baseball"      :   "",
        "NBA"           :   "",
        "Gossiping"     :   "",
        "Lifeismoney"   :   "",
        "Stock"         :   "",
        "give"          :   "",
        "Test"          :   "",
        "Broad_Band"    :   "今網"
    }
    url = 'https://www.ptt.cc'
    deny_pattern = re.compile(deny)
    while(True):
        time.sleep(random.randint(3, 10))
        allow_pattern = re.compile(allow[board])
        web = requests.get('https://www.ptt.cc/bbs/'+board+'/index.html', cookies={'over18':'1'})
        soup = BeautifulSoup(web.text, "html.parser")
        articles = soup.find_all('div', class_='title')     # 取得 class 為 title 的 div 內容
        for article in articles:
            if article.find('a') != None:
                title = article.find('a').get_text()
                if deny_pattern.search(title) == None or deny == "":
                    if allow_pattern.search(title) != None or allow[board] == "":
                        link = url+article.find('a')['href']
                        pt_db.insert_to_database(channel_id[board], board, title, link )
def telegram_alert_on_new():
    records = pt_db.retrieve_updates_after_time()
    msg = "%s"
    msg = "<a href='%s'>%s</a>"
    for record in records:
        format_msg = msg % (
            record['link'],
            record['title']
        )
        result = pt_bot.send(format_msg,record['chat_id'])
        if isinstance(result, Message):
            pt_db.update_tg_notify_time(record['_id'])
