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

from telegram import Message
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

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