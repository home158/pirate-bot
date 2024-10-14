from flask import Flask
import threading
import os
import time
import pt_bot
import pt_config

app = Flask(__name__)
@app.route("/")

def run_web_app():
    port = int(os.environ.get("PORT", "8443"))
    app.run("127.0.0.1", port)


if __name__ == "__main__":
    if pt_config.TELEGRAM_BOT_MODE == "polling":

        pass
    else:
        run_web_app()
