# coding: utf-8
import logging
from datetime import datetime
import pt_config
import json
from pymongo import MongoClient
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ChatAction
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Application, ContextTypes, filters, CallbackQueryHandler, )
import time
from telegram import Message
from telegram.error import RetryAfter
import asyncio
import inspect

# 使用 pt_logger 設定日誌
import pt_logger

application = Application.builder().token(pt_config.BOT_TOKEN).build()

bot_event_loop = asyncio.new_event_loop()
logger = pt_logger.logger


def send(msg, chat_id):
    while True:
        try:
            # Send the message and wait for the result
            result = bot_event_loop.run_until_complete(application.bot.sendMessage(chat_id=chat_id, text=msg, parse_mode='html'))
            if isinstance(result, Message):
                return result  # Successfully sent, return the message object
            else:
                print("Result is not a Message object:", result)
                break  # Exit if the result is not as expected
        except RetryAfter as e:
            # Handle the RetryAfter exception specifically
            wait_time = e.retry_after  # Get the wait time from the exception
            logger.warning(f"Flood control exceeded. Retrying in {wait_time} seconds.")
            time.sleep(wait_time)  # Wait for the specified time before retrying
        except Exception as e:
            # Catch all other exceptions
            logger.error("Send message and caught an exception.", exc_info=True)
            break  # Exit the loop on unexpected errors

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = f'''
            /my 顯示追蹤清單
            /clearall 清空全部追蹤清單
            /clear 刪除指定追蹤商品
            /add 後貼上momo商品連結可加入追蹤清單
            或是可以直接使用指令選單方便操作
            ====
            '''
    await update.message.reply_text(text=inspect.cleandoc(message))


def _register_bot_command_handler():
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)


_register_bot_command_handler()
