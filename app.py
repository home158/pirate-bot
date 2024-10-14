import threading
import time
import pt_logger  # 導入日誌配置
import pt_scheduler
import pt_config
import pt_bot

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

if __name__ == "__main__":
    if pt_config.TELEGRAM_BOT_MODE == "polling":
        logger.info("Starting threads in polling mode...")
        
        boards = ["NBA", "Gossiping", "Lifeismoney", "Baseball", "give", "Broad_Band"]
        threads = []
        for board in boards:
            thread = PttCrawleFetcherThread(board)
            thread.start()
            threads.append(thread)  # 儲存線程以便後續操作
            logger.info(f"Started PttCrawleFetcherThread for board: {board}")

        alert_thread = TelegramAlertSchedulerThread()
        alert_thread.start()
        logger.info("Started TelegramAlertSchedulerThread.")
        
        pt_bot.application.run_polling()
        logger.info("Telegram bot polling started.")

        # 可選：等待所有 PTT 爬蟲線程結束
        for thread in threads:
            thread.join()
    else:
        logger.info("Running in web app mode...")
