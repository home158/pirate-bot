from flask import Flask
import threading
import os
import time
import pt_bot
import pt_config
import pt_scheduler
app = Flask(__name__)
@app.route("/")

def run_web_app():
    port = int(os.environ.get("PORT", "8443"))
    app.run("127.0.0.1", port)

class TelegramAlertSchedulerThread(threading.Thread):
    def run(self) -> None:
        while True:
            try:
                pt_scheduler.telegram_alert_on_new()
                time.sleep(pt_config.TELEGRAM_SEND_MESSAGE_INTERVAL)
            except Exception as e:
                print(f"An error occurred: {e}")
                pass
class PttCrawleFetcherThread(threading.Thread):
    def __init__(self, board_name):
        super().__init__()
        self.board_name = board_name  # 將參數保存到實例屬性
        #self.tg_chat_id = tg_chat_id  # 將參數保存到實例屬性

    def run(self) -> None:
        while True:
            try:
                # 將參數傳遞給 pt_scheduler.ptt_crawler
                pt_scheduler.ptt_crawler(self.board_name)
            except Exception as e:
                print(f"An error occurred: {e}")
                pass

if __name__ == "__main__":
    if pt_config.TELEGRAM_BOT_MODE == "polling":
        # 在創建 PttCrawleFetcherThread 時傳入參數
        PttCrawleFetcherThread("NBA").start()
        PttCrawleFetcherThread("Gossiping").start()
        PttCrawleFetcherThread("Lifeismoney").start()
        PttCrawleFetcherThread("Baseball").start()
        PttCrawleFetcherThread("give").start()
        PttCrawleFetcherThread("Broad_Band").start()

        TelegramAlertSchedulerThread().start()
        pt_bot.application.run_polling()
    else:
        run_web_app()
