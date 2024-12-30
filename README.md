### 在本機端運行

- 在專案資料夾內建立一個檔名為 `.env` 檔案，內容如下
- 將 BOT_TOKEN 內容變更為建立 Telegram bot 時取得的 Token

```text
BOT_TOKEN = "{replace_me}"
TELEGRAM_BOT_MODE = "polling"
TELEGRAM_NOTIFY_ONCE_COUNT = 5
TELEGRAM_NOTIFY_ONCE_COUNT = 5
TELEGRAM_SEND_MESSAGE_INTERVAL = 8
GMAIL_SEND_MESSAGE_INTERVAL = 5
CHROMEDRIVER_REQUEST_INTERVAL = 23
MONGO_DB_SERVER ="mongodb://127.0.0.1:27017/"
CHROME_BINARY_PATH = '.\\chrome\\128\\chrome-headless-shell-win64\\chrome-headless-shell.exe'
_CHROME_BINARY_PATH = '.\\chrome\\128\\chrome-win64\\chrome.exe'
CHROMEDRIVER_EXECUTABLE_PATH = ".\\chrome\\128\\chromedriver-win64\\chromedriver.exe"
ENABLE_CONSOLE_LOGGING = True
LOG_LEVEL=INFO
GMAIL_AUTH_USER="{replace_me}"
GMAIL_AUTH_PASS="{replace_me}"
GMAIL_MAIL_TO="{replace_me}"
PTT_AUTH_USER="{replace_me}"
PTT_AUTH_PASS="{replace_me}"
PTTMAIL_AUTH_USER='{replace_me}'
PTTMAIL_AUTH_PASS='{replace_me}'
_NOTIFY_GMAIL_ONLY=beclass 台北科教館|beclass 2024八里城市沙雕展|beclass NISSAN|新北市政府觀光旅遊局|新北市政府觀光旅遊局- 最新消息|國立故宮博物院|北藝中心|天文科學教育館|桃園市立美術館|新北市立圖書館|新北市政府|兒童藝術教育中心|台北市立圖書館|新北PAY|金車關係事業活動網站
_NOTIFY_TG_ONLY=NBA|Lifeismoney|give|Broad_Band|Baseball|beclass 台北科教館|beclass 2024八里城市沙雕展|beclass NISSAN|新北市政府觀光旅遊局|新北市政府觀光旅遊局- 最新消息|國立故宮博物院|北藝中心|天文科學教育館|桃園市立美術館|新北市立圖書館|新北市政府|兒童藝術教育中心|台北市立圖書館|新北PAY|金車關係事業活動網站
NOTIFY_TG_ONLY=Stock|Lifeismoney
NOTIFY_GMAIL_ONLY=冬至湯圓親子手作活動|beclass 台北科教館|beclass 2024八里城市沙雕展|beclass NISSAN|新北市政府觀光旅遊局|新北市政府觀光旅遊局- 最新消息|國立故宮博物院|北藝中心|天文科學教育館|桃園市立美術館|新北市立圖書館|新北市政府|兒童藝術教育中心|台北市立圖書館|新北PAY|金車關係事業活動網站
WEB_CRAWLER_SOURCE_PATH = '.\\resource\\web_crawler_source.json'
_TERM_PTT_BOARD=Test
TERM_PTT_BOARD=Broad_Band
FACEBOOK_CRAWLER_SOURCE_PATH='.\\resource\\facebook_crawler_source.json'
FACEBOOK_AUTH_USER='{replace_me}'
FACEBOOK_AUTH_PASS='{replace_me}'
WEB_PTT_SOURCE_PATH='.\\resource\\web_ptt.json'
PTTMAIL_SKIP_LINE = '[公告]|[協尋]|本文已被吃掉|本文已被刪除|洽中|洽|勿來信|送出|已贈出|贈出|已完成|已徵得|已徵到|文章選讀|文章標題|看板資訊|看板'
PTTMAIL_KEYWORDS_ONLY = '測試簽名檔|推薦人今網|推薦今網|今網推薦|徵求今網|徵今網推薦人|徵今網業務|徵求一位今網推薦'
PTTMAIL_KEYWORDS_DENY = '已完成|完成|已徵得|徵得|已徵到|徵到'
PTTMAIL_KINGNET_MSG = "大大您好，\n在版上看到您在徵求"
```

- 下載舊版chromedriver及chrome的方法

```text
先查詢版本號ex:128.0.6613.86
https://www.chromedriverdownload.com/

找到下載連結取代版本號即可下載舊版
https://googlechromelabs.github.io/chrome-for-testing/

下載網址連結
https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.86/win64/chrome-headless-shell-win64.zip
https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.86/linux64/chrome-headless-shell-linux64.zip
https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.86/win64/chromedriver-win64.zip
https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.86/linux64/chromedriver-linux64.zip

```