import threading
import time
import argparse  # 用於解析命令行參數
import pt_logger  # 導入日誌配置
import pt_scheduler
import pt_config
import pt_bot
import pt_util
# 將 pt_logger.logger 賦值給 logger 變數
logger = pt_logger.logger

class TelegramAlertSchedulerThread(threading.Thread):
    def run(self) -> None:
        while True:
            try:
                pt_scheduler.telegram_alert_on_new()
                time.sleep(pt_config.TELEGRAM_SEND_MESSAGE_INTERVAL)
            except Exception as e:
                logger.error(f"An error occurred in TelegramAlertSchedulerThread: {e}")
class TelegramAlertSchedulerThread(threading.Thread):
    def run(self) -> None:
        while True:
            try:
                pt_scheduler.telegram_alert_on_new()
                time.sleep(pt_config.TELEGRAM_SEND_MESSAGE_INTERVAL)
            except Exception as e:
                logger.error(f"An error occurred in TelegramAlertSchedulerThread: {e}")
class PttMailSchedulerThread(threading.Thread):
    def run(self) -> None:
        while True:
            try:
                pt_scheduler.term_ptt_mailer()
                
                time.sleep(pt_config.PTT_MAIL_MESSAGE_INTERVAL)
            except Exception as e:
                logger.error(f"An error occurred in PttMailSchedulerThread: {e}")

class GmailSendSchedulerThread(threading.Thread):
    def run(self) -> None:
        while True:
            try:
                pt_scheduler.gmail_alert_on_new()
                time.sleep(pt_config.GMAIL_SEND_MESSAGE_INTERVAL)
            except Exception as e:
                logger.error(f"An error occurred in GmailSendSchedulerThread: {e}")

class PttCrawleFetcherThread(threading.Thread):
    def __init__(self, board_name):
        super().__init__()
        self.board_name = board_name

    def run(self) -> None:
        while True:
            try:
                pt_scheduler.ptt_crawler(self.board_name)
                logger.info(f"Successfully fetched data for board: {self.board_name}")
            except Exception as e:
                logger.error(f"An error occurred in PttCrawleFetcherThread for {self.board_name}: {e}")
class FacebookCrawleFetcherThread(threading.Thread):
    def run(self) -> None:
        while True:
            try:
                pt_scheduler.facebook_crawler()
            except Exception as e:
                logger.error(f"An error occurred in FacebookCrawleFetcherThread: {e}")

class WebCrawleFetcherThread(threading.Thread):
    def run(self) -> None:
        while True:
            try:
                pt_scheduler.web_crawler()
            except Exception as e:
                logger.error(f"An error occurred in WebCrawleFetcherThread: {e}")
class termPttFetcherThread(threading.Thread):
    def __init__(self, board_name):
        super().__init__()
        self.board_name = board_name

    def run(self) -> None:
        while True:
            try:
                if pt_scheduler.check_internet() is True:
                    pt_scheduler.term_ptt_crawler(self.board_name)
                    logger.info(f"Successfully fetched data for board: {self.board_name}")
                else:
                    logger.info(f"No network retry in 60 sec.")
                    time.sleep(60)
                    

            except Exception as e:
                logger.error(f"An error occurred in PttCrawleFetcherThread for {self.board_name}: {e}")
def run_threads_pttmail():
     #pt_scheduler.pttmail_on_new()    
    logger.info("Starting threads in ptt mail mode...")
    gmail_thread = PttMailSchedulerThread()
    gmail_thread.start()
    logger.info("ptt mail bot polling started.")

def run_threads_gmail():
    logger.info("Starting threads in Gmail mode...")
    gmail_thread = GmailSendSchedulerThread()
    gmail_thread.start()
    logger.info("Gmail bot polling started.")

def run_threads_tg():
    logger.info("Starting threads in telegram notify...")
    alert_thread = TelegramAlertSchedulerThread()
    alert_thread.start()
    logger.info("Started TelegramAlertSchedulerThread.")
    logger.info("Telegram bot telegram notify.")
    pt_bot.application.run_polling()

def run_threads_ptt():
    #pt_scheduler.term_ptt_crawler(pt_config.TERM_PTT_BOARD)    
    ptt_thread = termPttFetcherThread(pt_config.TERM_PTT_BOARD)
    ptt_thread.start()
    
    

def run_threads_webptt():
    boards = pt_util.read_json_file(pt_config.WEB_PTT_SOURCE_PATH)
    threads = []
    
    for board in boards:
        thread = PttCrawleFetcherThread(board)
        thread.start()
        threads.append(thread)
        logger.info(f"Started PttCrawleFetcherThread for board: {board}")



    for thread in threads:
        thread.join()

def run_threads_facebook():
    threads = []

    TpmlGovTaipei = FacebookCrawleFetcherThread()
    TpmlGovTaipei.start()
    threads.append(TpmlGovTaipei)

    for thread in threads:
        thread.join()

def run_threads_web():  
    threads = []

    TpmlGovTaipei = WebCrawleFetcherThread()
    TpmlGovTaipei.start()
    threads.append(TpmlGovTaipei)

    for thread in threads:
        thread.join()
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control the flow of the application.")
    
    # 添加 --mode 參數，預設為 'polling'
    parser.add_argument("--mode", type=str, default="polling", help="Execution mode: 'polling' or 'web'.")
    
    # 解析命令行參數
    args = parser.parse_args()



    # Switch-like structure using a dictionary
    switch = {
        "pttmail_notify": run_threads_pttmail,
        "gmail_notify": run_threads_gmail,
        "tg_notify": run_threads_tg,
        "web": run_threads_web,
        "facebook": run_threads_facebook,
        "webptt": run_threads_webptt,
        "termptt": run_threads_ptt
    }

    # Get the function based on the mode and call it, if the mode is valid
    switch.get(args.mode, lambda: print("Invalid mode"))()
