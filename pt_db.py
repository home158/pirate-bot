# coding: utf-8
import logging
from datetime import datetime

import pt_config
import json
from pymongo import MongoClient


def insert_to_database(chat_id = None, board = None, title= None, link= None ):
    client = MongoClient(pt_config.DB_SERVER)
    db = client.website
    website = db.pirate
    current_time = datetime.now()
    # Prepare the new product details
    product_details = {
        'board': board.strip(),
        'title': title.strip(),
        'link': link.strip(),
        'insert_time': current_time,
        'chat_id': chat_id,
        'tg_notify_time' : None
    }
    # Step 1: Check if a document with the same url, title and coupon exists
    existing_document = website.find_one({'board': product_details['board'], 'title': product_details['title'], 'link': product_details['link']})

    if existing_document is None:
        result = website.insert_one(product_details)
        print("No matching url found, new document inserted with id:", result.inserted_id)
        return True, product_details, current_time
    else:
        return False , current_time
def retrieve_updates_after_time():
    # 連接到 MongoDB
    client = MongoClient(pt_config.DB_SERVER)
    collection = client.website.pirate

    
    # 執行查詢
    documents = collection.find({ "tg_notify_time": None }).limit(pt_config.TELEGRAM_NOTIFY_ONCE_COUNT)
    # 將資料轉換為列表（JSON 陣列）
    json_array = [doc for doc in documents]


    return json_array  # 返回 JSON 陣列和 JSON 字串（如果需要）

def update_tg_notify_time(_id):
    client = MongoClient(pt_config.DB_SERVER)
    db = client.website
    website = db.pirate
    current_time = datetime.now()
    result = website.update_one(
        {'_id': _id},  # Match by url
        {'$set': { 'tg_notify_time': current_time}}  # Update tg_notify_time
    )
    if result.modified_count > 0:
        print(f"Document with _id {_id} was updated successfully.")
    else:
        print(f"No changes made to the document with _id {_id}.")
