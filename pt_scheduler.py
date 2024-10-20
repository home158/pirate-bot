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
import json
import os
import pt_gmail
from telegram import Message
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.keys import Keys
import socket

# 使用 pt_logger 設定日誌
import pt_logger
channel_id = {}
logger = pt_logger.logger
def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def check_internet(host="8.8.8.8", port=53, timeout=1):  # Timeout set to 1 second for fast response
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as e:
        logger.error(f"No network: {e}")
        return False



def ptt_crawler(board):
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
        tg_only = pt_config.NOTIFY_TG_ONLY.split("|")
        records = pt_db.retrieve_updates_after_time("tg_notify_time",tg_only)
        msg_template = "<a href='%s'>%s</a>"

        for record in records:
            format_msg = msg_template % (record['link'], record['title'])
            result = pt_bot.send(format_msg, record['chat_id'])

            if isinstance(result, Message):
                pt_db.update_notify_time("tg_notify_time",record['_id'])
                logger.info(f"Notification sent for: {record['title']}")
            else:
                logger.error(f"Failed to send message for: {record['title']}")

    except Exception as e:
        logger.error(f"Error sending Telegram or gmail notifications: {e}")
def gmail_alert_on_new():
    try:
        gmail_only = pt_config.NOTIFY_GMAIL_ONLY.split("|")

        records = pt_db.retrieve_updates_after_time("gmail_notify_time",gmail_only)
        msg_template = "<a href='%s'>%s</a>"

        for record in records:
            format_msg = msg_template % (record['link'], record['title'])
            result = pt_gmail.send(record['title'], format_msg)
            if result is True:
                pt_db.update_notify_time("gmail_notify_time",record['_id'])
    except Exception as e:
        logger.error(f"Error sending Telegram or gmail notifications: {e}")
def handle_selenium_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TimeoutException as timeout_err:
            print(f"Timeout occurred while loading page: {timeout_err}")
        except NoSuchElementException as no_elem_err:
            print(f"Element not found: {no_elem_err}")
        except WebDriverException as driver_err:
            print(f"WebDriver error occurred: {driver_err}")
        except ConnectionError as conn_err:
            print(f"Network connection error occurred: {conn_err}")
        except Exception as err:
            print(f"An unexpected error occurred: {err}")
    return wrapper

def init_driver():

    chromedriver_executable_path = pt_config.CHROMEDRIVER_EXECUTABLE_PATH

    # 设置无头模式
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # 指定 Chrome 可执行文件路径
    chrome_options.binary_location = pt_config.CHROME_BINARY_PATH


    # 启动 Chrome
    service = Service(executable_path=chromedriver_executable_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1920,1080)

    return driver
def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        return json_data
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None
def take_screenshot(driver, file_name):
    """保存当前页面截图"""
    screenshots_dir = 'screenshots'
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)  # 创建文件夹存放截图

    file_path = os.path.join(screenshots_dir, f"{file_name}.png")
    driver.save_screenshot(file_path)
    print(f"截图已保存到: {file_path}")

@handle_selenium_errors
def fetch_requests(driver, item):
    url = item.get('url')
    note = item.get('note')
    chat_id = item.get('chat_id')
    parent_css_selector = item.get("css_selector")[0]
    child_css_selector = item.get("css_selector")[1]
    link_css_selector = item.get("css_selector")[2]
    driver.get(url)

    # Wait for the body element to be present before proceeding
    time.sleep(3)
    wait_for_body_to_load(driver)
    # Find parent elements using the specified CSS selector
    parent_elements = driver.find_elements(By.CSS_SELECTOR, parent_css_selector)

    # Iterate through the parent elements and retrieve child element information
    for parent_element in parent_elements:
        process_parent_element(chat_id, note, parent_element, child_css_selector,link_css_selector)

    take_screenshot(driver, f"{note}")

def wait_for_body_to_load(driver):
    """Wait until the body element is present in the DOM."""
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))
    )

def process_parent_element(chat_id, note, parent_element, child_css_selector,link_css_selector):
    """Retrieve the text and child element href from the parent element."""
    try:
        child_element = parent_element.find_element(By.CSS_SELECTOR, child_css_selector)
        if link_css_selector == 'self':
            link_element = parent_element
        else:
            link_element = parent_element.find_element(By.CSS_SELECTOR, link_css_selector)
        title = child_element.text
        link = link_element.get_attribute('href')
        print(f"Parent Element Text: {title}")
        print(f"Child Element Href: {link}")
        pt_db.insert_to_database(chat_id, note, title, link)
    except Exception as e:
        print(f"Error processing parent element: {e}")

def web_crawler():
        driver = init_driver()
        try:
            web_source = read_json_file('web_crawler_source.json')
            if web_source:
                # For loop to iterate over the JSON array
                for item in web_source:
                    fetch_requests(driver,item)


        except Exception as e:
            # 捕获其他异常
            print(f"总体处理时发生错误: {e}")

        finally:
            driver.quit()
def keyAndPressEnter(driver , key_text):
    actions = ActionChains(driver)
    actions.send_keys(key_text).perform()
    time.sleep(3)
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(3)

def check_point(driver , row , wishtext):
    elem = driver.find_element(By.CSS_SELECTOR, "#mainContainer > span:nth-child("+str(row)+")")
    logger.info(elem.text)

    if wishtext in elem.text.strip():
        return True
    else:
        return False
def extract_labels_and_contents(log_text):
    pattern = r'□\s*(.*)'
    
    # Split the log text into lines
    lines = log_text.strip().split('\n')
    
    # Create a list to store the results
    results = []

    # Process each line
    for line in lines:
        # Check if the line contains [公告] or [協尋]
        if '[公告]' in line or '[協尋]' in line or '本文已被刪除' in line or '洽中' in line or '洽' in line or '勿來信' in line or '送出' in line or '已贈出' in line or '贈出' in line:
            continue  # Skip this line
        
        # Find matches in the line
        matches = re.findall(pattern, line)

        # Process the matches
        for match in matches:
            content = match.strip()  # Clean up the matched content
            results.append(content)

    return results
def checkIsOnline(driver):
    elem = driver.find_element(By.CSS_SELECTOR, "#reactAlert")
    if "你斷線了" in elem.text.strip():
        return True
    else:
        return False
@handle_selenium_errors
def term_ptt_crawler(board):

    article_lists = []

    driver = init_driver()
    driver.get("https://term.ptt.cc/")
    time.sleep(10)

    if check_point(driver, 21 , "請輸入代號，或以 guest 參觀，或以 new 註冊:"):
        keyAndPressEnter(driver , pt_config.PTT_AUTH_USER)
        if check_point(driver, 22 , "請輸入您的密碼:"):
            keyAndPressEnter(driver , pt_config.PTT_AUTH_PASS)

    if check_point(driver, 23 , "正在更新與同步線上使用者及好友名單，系統負荷量大時會需時較久..."):
        time.sleep(30)

    if check_point(driver, 23 , "您想刪除其他重複登入的連線嗎？[Y/n]"):
        keyAndPressEnter(driver , 'Y')

    
    ActionChains(driver).send_keys('q').perform()
    time.sleep(1)
    ActionChains(driver).send_keys('q').perform()
    time.sleep(1)
    ActionChains(driver).send_keys('q').perform()
    time.sleep(1)
    if check_point(driver, 1 , "【主功能表】"):
        ActionChains(driver).send_keys('s').perform()
        ActionChains(driver).send_keys(board).perform()
        time.sleep(1)
        ActionChains(driver).send_keys(Keys.ENTER).perform()
        time.sleep(1)                    
        if check_point(driver, 24 , "請按任意鍵繼續"):
            ActionChains(driver).send_keys('q').perform()
            time.sleep(1)
        if check_point(driver, 24 , "其它任意鍵停止"):
            ActionChains(driver).send_keys('q').perform()
            time.sleep(1)
        while True:
            if checkIsOnline(driver) is True:
                driver.quit()
                break
            ActionChains(driver).send_keys(Keys.HOME).perform()
            ActionChains(driver).send_keys(Keys.END).perform()
            time.sleep(1)
            row_18 = driver.find_element(By.CSS_SELECTOR, "#mainContainer")
            results = extract_labels_and_contents(row_18.text)
            for title in results:
                if title not in article_lists:
                    pt_db.insert_to_database(channel_id[board], board, title )
                    article_lists.append(title)
            logger.info(article_lists)
            
channel_id = read_json_file('tg_channel_id.json')
