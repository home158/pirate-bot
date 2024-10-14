
import requests
from bs4 import BeautifulSoup
import re
import telegram
import asyncio
import time
import random
import platform
boards = ["NBA","Lifeismoney","give","Broad_Band"]

channel_id = {
    "NBA"           :   "YOUR_CHANNEL_ID",
    "Gossiping"     :   "YOUR_CHANNEL_ID",
    "Lifeismoney"   :   "YOUR_CHANNEL_ID",
    "give"          :   "YOUR_CHANNEL_ID",
    "Test"          :   "YOUR_CHANNEL_ID",
    "Broad_Band"    :   "YOUR_CHANNEL_ID"
}
my_token = "YOUR_TOKEN"

deny = "公告|協尋"
allow = {
    "NBA" :   "",
    "Gossiping" :   "",
    "Lifeismoney" : "",
    "Stock" :       "",
    "give" :        "",
    "Test" :        "",
    "Broad_Band" :  "今網"
}
storage = {
    "NBA" :   [],
    "Gossiping" :   [],
    "Lifeismoney" : [],
    "Stock" :       [],
    "give" :        [],
    "Test" :        [],
    "Broad_Band" :  []
}

url = 'https://www.ptt.cc'
async def send(msg, chat_id, href ):
    bot = telegram.Bot(token=my_token)
    msg = re.sub('[<>]',"",msg)
    bot.sendMessage(chat_id=chat_id, text="<a href='"+url+href+"'>"+msg+"</a>", parse_mode='html')



deny_pattern = re.compile(deny)

max_storage_size = 30
max_telegram_message_once = 7


def indexof( array, elem):
    try:
        return array.index(elem)
    except ValueError:
        return -1

i = True
while(i == True):
    time.sleep(random.randint(3, 10))
    for board in boards:
        allow_pattern = re.compile(allow[board])
        web = requests.get('https://www.ptt.cc/bbs/'+board+'/index.html', cookies={'over18':'1'})
        soup = BeautifulSoup(web.text, "html.parser")
        articles = soup.find_all('div', class_='title')     # 取得 class 為 title 的 div 內容
        msg_count=0
        for article in articles:
            if article.find('a') != None:
                title = article.find('a').get_text()
                if deny_pattern.search(title) == None or deny == "":
                    if allow_pattern.search(title) != None or allow[board] == "":
                        #print(title)
                        link = article.find('a')['href']
                        #print(url + link, end='\n')
                        if indexof(storage[board],link) == -1:
                            if msg_count < max_telegram_message_once:
                                storage[board].append(link)
                                asyncio.run(send(msg=title, chat_id=channel_id[board], href = link ))
                                msg_count+=1
                                if len(storage[board]) > max_storage_size:
                                    storage[board] = storage[board][1:]