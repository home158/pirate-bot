import logging
from datetime import datetime
import pt_config
import pt_db
import pt_bot
import time
import random
import requests
from bs4 import BeautifulSoup
import re
from telegram import Message

# 使用 pt_logger 設定日誌
import pt_logger

logger = pt_logger.logger

def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

    while True:
        try:
            time.sleep(random.randint(3, 10))
            allow_pattern = re.compile(allow[board])
            response = requests.get(f'https://www.ptt.cc/bbs/{board}/index.html', cookies={'over18': '1'})
            response.raise_for_status()  # 檢查 HTTP 狀態碼

            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all('div', class_='title')
            
            for article in articles:
                if article.find('a') is not None:
                    title = article.find('a').get_text()
                    if deny_pattern.search(title) is None or deny == "":
                        if allow_pattern.search(title) is not None or allow[board] == "":
                            link = url + article.find('a')['href']
                            logger.info(f"Fetched article: {title} - {link}")
                            pt_db.insert_to_database(channel_id[board], board, title, link)

        except requests.RequestException as e:
            logger.error(f"Error fetching PTT {board}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

def telegram_alert_on_new():
    try:
        records = pt_db.retrieve_updates_after_time()
        msg_template = "<a href='%s'>%s</a>"

        for record in records:
            format_msg = msg_template % (record['link'], record['title'])
            result = pt_bot.send(format_msg, record['chat_id'])

            if isinstance(result, Message):
                pt_db.update_tg_notify_time(record['_id'])
                logger.info(f"Notification sent for: {record['title']}")
            else:
                logger.error(f"Failed to send message for: {record['title']}")

    except Exception as e:
        logger.error(f"Error sending Telegram notifications: {e}")
