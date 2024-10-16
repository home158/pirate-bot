# coding: utf-8
import logging
from datetime import datetime
from pymongo import MongoClient
import pt_config
import pt_logger  # 引入你配置的日誌系統

logger = pt_logger.logger

# 初始化 MongoDB 連接
client = MongoClient(pt_config.DB_SERVER)
db = client.website
website = db.pirate

def insert_to_database(chat_id=None, board=None, title=None, link=None):
    current_time = datetime.now()
    
    # 準備新文章資料
    product_details = {
        'board': board.strip(),
        'title': title.strip(),
        'link': link,
        'insert_time': current_time,
        'chat_id': chat_id,
        'tg_notify_time': None
    }
    
    try:
        # Step 1: 檢查是否存在相同的文章
        existing_document = website.find_one({
            'board': product_details['board'],
            'title': product_details['title'],
            'link': product_details['link']
        })

        if existing_document is None:
            result = website.insert_one(product_details)
            logger.info(f"Inserted new document with id: {result.inserted_id}")
            return True, product_details, current_time
        else:
            logger.info(f"Duplicate document found, no insert performed.")
            return False, current_time
    except Exception as e:
        logger.error(f"Error inserting document: {e}")
        return False, current_time

def retrieve_updates_after_time():
    try:
        # 查詢 tg_notify_time 為 None 的文章
        documents = website.find({"tg_notify_time": None}).limit(pt_config.TELEGRAM_NOTIFY_ONCE_COUNT)
        json_array = [doc for doc in documents]  # 轉換為 JSON 列表
        
        logger.info(f"Retrieved {len(json_array)} documents for notification.")
        return json_array
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        return []

def update_tg_notify_time(_id):
    current_time = datetime.now()
    try:
        result = website.update_one(
            {'_id': _id},  # 根據 _id 匹配文件
            {'$set': {'tg_notify_time': current_time}}  # 更新通知時間
        )
        if result.modified_count > 0:
            logger.info(f"Document with _id {_id} was updated successfully.")
        else:
            logger.warning(f"No changes made to the document with _id {_id}.")
    except Exception as e:
        logger.error(f"Error updating document with _id {_id}: {e}")
