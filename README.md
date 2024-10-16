### 在本機端運行

- 在專案資料夾內建立一個檔名為 `.env` 檔案，內容如下
- 將 BOT_TOKEN 內容變更為建立 Telegram bot 時取得的 Token

```text
BOT_TOKEN = "{replace_me}"
TELEGRAM_BOT_MODE = "polling"
TELEGRAM_NOTIFY_ONCE_COUNT = 5
TELEGRAM_NOTIFY_ONCE_COUNT = 5
TELEGRAM_SEND_MESSAGE_INTERVAL = 8
CHROMEDRIVER_REQUEST_INTERVAL = 23
MONGO_DB_SERVER ="mongodb://127.0.0.1:27017/"
CHROME_BINARY_PATH = '.\\chrome\\128\\chrome-headless-shell-win64\\chrome-headless-shell.exe'
_CHROME_BINARY_PATH = '.\\chrome\\128\\chrome-win64\\chrome.exe'
CHROMEDRIVER_EXECUTABLE_PATH = ".\\chrome\\128\\chromedriver-win64\\chromedriver.exe"
ENABLE_CONSOLE_LOGGING = True
LOG_LEVEL=INFO

```
