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
import os
import pt_gmail
import pt_util
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
import asyncio
from selenium.webdriver.remote.webdriver import WebDriver

# 使用 pt_logger 設定日誌
import pt_logger
channel_id = pt_util.read_json_file('./resource/tg_channel_id.json')
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
            format_msg = msg_template % (record['link'], record['title'].replace('<', '').replace('>', ''))
            result = pt_bot.send(format_msg, record['chat_id'])

            if isinstance(result, Message):
                pt_db.update_notify_time("tg_notify_time",record['_id'])
                logger.info(f"Notification sent for: {record['title']}")
            else:
                logger.error(f"Failed to send message for: {record['title']}")

    except Exception as e:
        logger.error(f"Error sending Telegram or gmail notifications: {e}")
def pttmail_on_new():
    try:
        keywords = pt_config.PTTMAIL_KEYWORDS_ONLY.split("|")
        logger.info(keywords)
        records = pt_db.retrieve_updates_after_time_keywords("pttmail_notify_time",keywords)
        logger.info(records)
        if len(records) > 0 :
            term_ptt_mailer(records)
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
    chrome_options.add_argument("--disable-notifications")

    # 指定 Chrome 可执行文件路径
    chrome_options.binary_location = pt_config.CHROME_BINARY_PATH


    # 启动 Chrome
    service = Service(executable_path=chromedriver_executable_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1920,1080)

    return driver
def take_screenshot(driver, file_name):
    """保存当前页面截图"""
    screenshots_dir = 'screenshots'
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)  # 创建文件夹存放截图

    file_path = os.path.join(screenshots_dir, f"{file_name}.png")
    driver.save_screenshot(file_path)
    print(f"截图已保存到: {file_path}")
def get_element_by_classname(driver,classname):
    # 使用多行 JavaScript 代码
    script = """
        var elArray = [];
        var tmp = document.getElementsByTagName("*");
        var regex = new RegExp(arguments[0]);
        for ( var i = 0; i < tmp.length; i++ ) {
            if ( regex.test(tmp[i].className) ) {
                elArray.push(tmp[i]);
            }
        }
        if(elArray.length > 0)
            return elArray[0].innerText;
        else
            return "";
    """

    # 执行脚本并返回结果
    price = driver.execute_script(script,classname)
    return price

@handle_selenium_errors
def fetch_facebook_requests(driver):
    async def login_facebook(driver, fb_username, fb_userpass):
        fb_login_url = 'https://mbasic.facebook.com/login'  # FB login page
        driver.get(fb_login_url)  # Open the Facebook login page
        take_screenshot(driver, "FACEBOOK")
        # Fill in Facebook login information
        fb_email_ele = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="email"]'))
        )
        fb_email_ele.send_keys(fb_username)
        fb_pass_ele = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="pass"]'))
        )
        fb_pass_ele.send_keys(fb_userpass)

        # Find the login button and click it
        login_ele = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="loginbutton"]'))
        )
        login_ele.click()
        time.sleep(10)
        take_screenshot(driver, "FACEBOOK")
        driver.get("https://mbasic.facebook.com/taipeilibrary?v=timeline")
        time.sleep(5)
        counter = 0
        while counter <= 10:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            counter += 1
            take_screenshot(driver, "FACEBOOK_scroll_"+str(counter))

        page_content = driver.page_source

        # 因為要解析的對象是 HTML，所以需指定 html.parser 解析器
        soup = BeautifulSoup(page_content, 'html.parser')
        elements = soup.select('.x1yztbdb.x1n2onr6.xh8yej3.x1ja2u2z')

        for element in elements:
            try:
                name = element.select('.html-div.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd').text
                
                # 👇使用 a 標籤的效果一樣，但 CSS Selector 相比之下長很多
                # name = element.select('.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.xt0b8zv.xzsf02u.x1s688f span')[0].text
                print(name)
            except:
                continue



    asyncio.run(login_facebook(driver, pt_config.FACEBOOK_AUTH_USER ,pt_config.FACEBOOK_AUTH_PASS))

#   
#   
#   # Wait for an element that appears only after logging in to confirm login was successful
#   WebDriverWait(driver, 10).until(
#       EC.presence_of_element_located((By.XPATH, '//*[@id="objects_container"]'))
#    )

@handle_selenium_errors
def fetch_requests(driver, item):
    url = item.get('url')
    note = item.get('note')
    chat_id = item.get('chat_id')
    parent_css_selector = item.get("css_selector")[0]
    driver.get(url)

    # Wait for the body element to be present before proceeding
    time.sleep(3)
    wait_for_body_to_load(driver)


    # Find parent elements using the specified CSS selector
    if len(item.get("css_selector") )> 1 :
        text_css_selector = item.get("css_selector")[1]
        link_css_selector = item.get("css_selector")[2]
        parent_elements = driver.find_elements(By.CSS_SELECTOR, parent_css_selector)
        # Iterate through the parent elements and retrieve child element information
        for parent_element in parent_elements:
            process_parent_element(chat_id, note, parent_element, text_css_selector, link_css_selector)
    else:
        parent_element = driver.find_element(By.CSS_SELECTOR, parent_css_selector)
        pt_db.insert_to_database(chat_id, note, parent_element.text, url)

    take_screenshot(driver, f"{note}")

def wait_for_body_to_load(driver):
    """Wait until the body element is present in the DOM."""
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))
    )

def process_parent_element(chat_id, note, parent_element, text_css_selector,link_css_selector):
    """Retrieve the text and child element href from the parent element."""
    try:
        child_element = parent_element.find_element(By.CSS_SELECTOR, text_css_selector)
        if link_css_selector == 'self':
            link_element = parent_element
        else:
            link_element = parent_element.find_element(By.CSS_SELECTOR, link_css_selector)
        title = child_element.text
        link = link_element.get_attribute('href')
        print(f"Element: {title} {link}")
        pt_db.insert_to_database(chat_id, note, title, link)
    except Exception as e:
        print(f"Error processing parent element: {e}")
def facebook_crawler():
    driver = init_driver()
    try:
        fetch_facebook_requests(driver)
        #web_source = pt_util.read_json_file(pt_config.FACEBOOK_CRAWLER_SOURCE_PATH)
        #if web_source:
        #    # For loop to iterate over the JSON array
        #    for item in web_source:
                
    except Exception as e:
        # 捕获其他异常
        print(f"总体处理时发生错误: {e}")
    finally:
        driver.quit()

def web_crawler():
        driver = init_driver()
        try:
            web_source = pt_util.read_json_file(pt_config.WEB_CRAWLER_SOURCE_PATH)
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

def check_point(driver: WebDriver, row: int, wishtext: str) -> bool:
    try:
        # Wait for the element to be present up to 10 seconds
        element_selector = f"#mainContainer > span:nth-child({row})"
        for attempt in range(5):
            try:
                elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, element_selector))
                )
                logger.info(f"Attempt {attempt + 1}: {elem.text}")

                # Check if the desired text is in the element's text
                if wishtext in elem.text.strip():
                    return True
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {e}")
            
            # Retry after 1 second delay
            time.sleep(1)

    except Exception as e:
        logger.error(f"Failed to locate element: {e}")

    return False
def extract_labels_and_contents(log_text):
    pattern = r'(\d+)\s+.*\s+([^\s]+)\s+([□R:]+)\s*(.*)'

    # Split the log text into lines
    lines = log_text.strip().split('\n')
    
    # Create a list to store the results
    results = []

    # Process each line
    for line in lines:
#        # Check if the line contains [公告] or [協尋]
        if '[公告]' in line or '[協尋]' in line or '本文已被吃掉' in line or '本文已被刪除' in line or '洽中' in line or '洽' in line or '勿來信' in line or '送出' in line or '已贈出' in line or '贈出' in line:
            continue  # Skip this line
        match = re.search(pattern, line)
        
        if match:  # 檢查是否匹配成功
            result = {
                "id": int(match.group(1)),
                "author": match.group(2),
                "content": match.group(4).strip(),  # 將 'R:' 和內容組合起來
                "title": match.group(4).strip()+f" ({match.group(2)})"
            }
            if is_alphanumeric(result['author']):
                logger.info(result)
                results.append(result)
        else:
            logger.info(f"無法匹配這一行: {line}")  # 可以選擇打印無法匹配的行進行調試

    return results
def checkIsOnline(driver):
    elem = driver.find_element(By.CSS_SELECTOR, "#reactAlert")
    if "你斷線了" in elem.text.strip():
        return True
    else:
        logger.info("PTT is online")
        return False
def get_page_article_id(driver):
    pattern = r'(\d+)\s+.*\s+([^\s]+)\s+([□R:]+)\s*(.*)'
    try:
        # Wait for the element to be present up to 10 seconds
        for attempt in range(5):
            try:
                elem = driver.find_element(By.CSS_SELECTOR, "#mainContainer > span:nth-child(4)")
                line = elem.text.strip()
                # Check if the desired text is in the element's text
                match = re.search(pattern, line)
                id =  int(match.group(1))
                return id
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {e}")
            
            # Retry after 1 second delay
            time.sleep(1)

    except Exception as e:
        logger.error(f"Failed to locate element: {e}")

    return False

def is_alphanumeric(text):
    return bool(re.fullmatch(r'[a-zA-Z0-9]+', text))

@handle_selenium_errors
def term_ptt_crawler(board):

    article_lists = []

    driver = init_driver()
    driver.get("https://term.ptt.cc/")
    time.sleep(10)
    if check_point(driver, 21 , "請輸入代號，或以 guest 參觀，或以 new 註冊:"):
        logger.info(pt_config.PTT_AUTH_USER2)
        keyAndPressEnter(driver , pt_config.PTT_AUTH_USER2)
        if check_point(driver, 22 , "請輸入您的密碼:"):
            keyAndPressEnter(driver , pt_config.PTT_AUTH_PASS2)

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

            
            ActionChains(driver).key_down(Keys.HOME).key_up(Keys.HOME).perform()
            time.sleep(1)
            article_id = get_page_article_id(driver)
            logger.info("home目前頁面文章序號: " +str(article_id))
            if article_id < 21:
                ActionChains(driver).key_down(Keys.END).key_up(Keys.END).perform()
                time.sleep(2)
                article_id = get_page_article_id(driver)
            logger.info("end目前頁面文章序號: " +str(article_id))

            row_18 = driver.find_element(By.CSS_SELECTOR, "#mainContainer")
            results = extract_labels_and_contents(row_18.text)

            for result in results:
                title = result['title']
                if title not in article_lists:
                    pt_db.insert_to_database(
                        chat_id=channel_id[board], 
                        board=board, 
                        title=title,
                        author=result['author']
                    )
                    article_lists.append(title)
            logger.info(article_lists)
            
def copyTextToClipboard(driver,text_to_copy):
    script = """
        const textArea = document.createElement("textarea");
        textArea.value = arguments[0];  // 使用 arguments[0] 傳遞變數
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand("copy");
            console.log("文字已成功複製到剪貼板！");
        } catch (err) {
            console.error("無法複製文字：", err);
        }
        document.body.removeChild(textArea);

    """
    driver.execute_script(script,text_to_copy)

def input_chinese(driver,text_to_copy,delay_time = 1):
    copyTextToClipboard(driver,text_to_copy)
    ActionChains(driver).click().key_down(Keys.SHIFT).key_down(Keys.INSERT).key_up(Keys.INSERT).key_up(Keys.SHIFT).perform()
    time.sleep(delay_time)
    ActionChains(driver).send_keys(Keys.ENTER).perform()


@handle_selenium_errors
def term_ptt_mailer(records):


    driver = init_driver()
    driver.get("https://term.ptt.cc/")
    time.sleep(10)

    if check_point(driver, 21 , "請輸入代號，或以 guest 參觀，或以 new 註冊:"):
        logger.info(pt_config.PTT_AUTH_USER)
        keyAndPressEnter(driver , pt_config.PTT_AUTH_USER)
        if check_point(driver, 22 , "請輸入您的密碼:"):
            keyAndPressEnter(driver , pt_config.PTT_AUTH_PASS)

    if check_point(driver, 23 , "正在更新與同步線上使用者及好友名單，系統負荷量大時會需時較久..."):
        time.sleep(30)
        ActionChains(driver).send_keys('q').perform()

    if check_point(driver, 23 , "您想刪除其他重複登入的連線嗎？[Y/n]"):
        keyAndPressEnter(driver , 'Y')

    keyAndPressEnter(driver , "q")

    ActionChains(driver).send_keys('q').perform()
    time.sleep(1)
    ActionChains(driver).send_keys('q').perform()
    time.sleep(1)
    ActionChains(driver).send_keys('q').perform()
    time.sleep(1)
    if check_point(driver, 1 , "【主功能表】"):
        ActionChains(driver).send_keys('m').perform()
        time.sleep(1)
        ActionChains(driver).send_keys(Keys.ENTER).perform()
        time.sleep(1)
    for record in records:
        if checkIsOnline(driver) is True:
            driver.quit()
        if check_point(driver, 1 ,"電子郵件"):
            ActionChains(driver).send_keys('s').perform()
            time.sleep(1)
            ActionChains(driver).send_keys(Keys.ENTER).perform()
            time.sleep(1)

        if check_point(driver , 1 , "站內寄信"):
            if check_point(driver , 2 , "請輸入使用者代號"):
                #ActionChains(driver).send_keys(record['author']).perform()
                ActionChains(driver).send_keys('idl5185').perform()
                time.sleep(1)
                ActionChains(driver).send_keys(Keys.ENTER).perform()
                time.sleep(1)
            if check_point(driver , 3 , "主題"):
                input_chinese(driver,"Re: "+f"{record['title']}",1)
                input_chinese(driver,pt_config.PTTMAIL_KINGNET_MSG ,2)
                ActionChains(driver).click().key_down(Keys.CONTROL).key_down('x').key_up('x').key_up(Keys.CONTROL).perform()
                time.sleep(3)

            if check_point(driver , 1 , "檔案處理"):
                ActionChains(driver).send_keys(Keys.ENTER).perform()
                time.sleep(3)

            if check_point(driver , 1 , "請選擇簽名檔"):
                ActionChains(driver).send_keys(Keys.ENTER).perform()
                time.sleep(3)
            
            if check_point(driver , 23 , "已順利寄出"):
                pt_db.update_notify_time("pttmail_notify_time",record['_id'])
                logger.info(f"pttmail sent for: {record['title']}")

                ActionChains(driver).send_keys('y').perform()
                ActionChains(driver).send_keys(Keys.ENTER).perform()
                time.sleep(3)
            if check_point(driver , 24 , "請按任意鍵繼續"):
                ActionChains(driver).send_keys(Keys.ENTER).perform()
                time.sleep(3)

@handle_selenium_errors
def term_ptt_mailer_inner_loop():
    driver = init_driver()
    driver.get("https://term.ptt.cc/")
    time.sleep(10)

    if check_point(driver, 21 , "請輸入代號，或以 guest 參觀，或以 new 註冊:"):
        logger.info(pt_config.PTT_AUTH_USER)
        keyAndPressEnter(driver , pt_config.PTT_AUTH_USER)
        if check_point(driver, 22 , "請輸入您的密碼:"):
            keyAndPressEnter(driver , pt_config.PTT_AUTH_PASS)

    if check_point(driver, 23 , "正在更新與同步線上使用者及好友名單，系統負荷量大時會需時較久..."):
        time.sleep(30)
        ActionChains(driver).send_keys('q').perform()

    if check_point(driver, 23 , "您想刪除其他重複登入的連線嗎？[Y/n]"):
        keyAndPressEnter(driver , 'Y')

    keyAndPressEnter(driver , "q")
    while True:
        if checkIsOnline(driver) is True:
            driver.quit()
            break

        ActionChains(driver).send_keys('q').perform()
        time.sleep(1)
        ActionChains(driver).send_keys('q').perform()
        time.sleep(1)
        ActionChains(driver).send_keys('q').perform()
        time.sleep(1)

        keywords = pt_config.PTTMAIL_KEYWORDS_ONLY.split("|")
        logger.info(keywords)
        records = pt_db.retrieve_updates_after_time_keywords("pttmail_notify_time",keywords)

        if len(records) > 0 :
            if check_point(driver, 1 , "【主功能表】"):
                ActionChains(driver).send_keys('m').perform()
                time.sleep(1)
                ActionChains(driver).send_keys(Keys.ENTER).perform()
                time.sleep(1)
            for record in records:
                if checkIsOnline(driver) is True:
                    driver.quit()
                if check_point(driver, 1 ,"電子郵件"):
                    ActionChains(driver).send_keys('s').perform()
                    time.sleep(1)
                    ActionChains(driver).send_keys(Keys.ENTER).perform()
                    time.sleep(1)

                if check_point(driver , 1 , "站內寄信"):
                    if check_point(driver , 2 , "請輸入使用者代號"):
                        #ActionChains(driver).send_keys(record['author']).perform()
                        ActionChains(driver).send_keys('idl5185').perform()
                        time.sleep(1)
                        ActionChains(driver).send_keys(Keys.ENTER).perform()
                        time.sleep(1)
                    if check_point(driver , 3 , "主題"):
                        input_chinese(driver,"Re: "+f"{record['title']}",1)
                        input_chinese(driver,pt_config.PTTMAIL_KINGNET_MSG ,2)
                        ActionChains(driver).click().key_down(Keys.CONTROL).key_down('x').key_up('x').key_up(Keys.CONTROL).perform()
                        time.sleep(3)

                    if check_point(driver , 1 , "檔案處理"):
                        ActionChains(driver).send_keys(Keys.ENTER).perform()
                        time.sleep(3)

                    if check_point(driver , 1 , "請選擇簽名檔"):
                        ActionChains(driver).send_keys(Keys.ENTER).perform()
                        time.sleep(3)
                    
                    if check_point(driver , 23 , "已順利寄出"):
                        pt_db.update_notify_time("pttmail_notify_time",record['_id'])
                        logger.info(f"pttmail sent for: {record['title']}")

                        ActionChains(driver).send_keys('y').perform()
                        ActionChains(driver).send_keys(Keys.ENTER).perform()
                        time.sleep(3)
                    if check_point(driver , 24 , "請按任意鍵繼續"):
                        ActionChains(driver).send_keys(Keys.ENTER).perform()
                        time.sleep(3)

