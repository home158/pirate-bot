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
    if title is None:
        logger.info(f"Title is none empty, no insert performed.")
        return False, current_time
    if title == "":
        logger.info(f"Title is none empty, no insert performed.")
        return False, current_time
    # 準備新文章資料
    product_details = {
        'board': board.strip(),
        'title': title.strip(),
        'link': link,
        'insert_time': current_time,
        'chat_id': chat_id,
        'tg_notify_time': None,
        'gmail_notify_time': None
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

def retrieve_updates_after_time(type,board_only):
    try:
        # 查詢 tg_notify_time 為 None 的文章
        documents = website.find(
            {
                type: None,
                "board": {
                    "$in": board_only
                }
            }
        ).limit(pt_config.TELEGRAM_NOTIFY_ONCE_COUNT)
        json_array = [doc for doc in documents]  # 轉換為 JSON 列表
        
        logger.info(f"Retrieved {len(json_array)} documents for notification.")
        return json_array
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        return []

def update_notify_time(type,_id):
    current_time = datetime.now()
    try:
        result = website.update_one(
            {'_id': _id},  # 根據 _id 匹配文件
            {'$set': {type: current_time}}  # 更新通知時間
        )
        if result.modified_count > 0:
            logger.info(f"Document with _id {_id} was updated successfully.")
        else:
            logger.warning(f"No changes made to the document with _id {_id}.")
    except Exception as e:
        logger.error(f"Error updating document with _id {_id}: {e}")

def delete_old_documents(board='Gossiping', limit=20):
    """
    刪除 MongoDB 集合中除了最新 N 筆資料以外的其他資料

    參數:
    - db_name: 資料庫名稱
    - collection_name: 集合名稱
    - field_name: 用於排序的字段名稱，預設為 '_id'
    - limit: 要保留的最新資料數量，預設為 20
    - mongo_uri: MongoDB 連線 URI，預設為 'mongodb://localhost:27017/'
    """

    collection = website
    field_name='_id'
    # 查找最新的 limit 筆資料，按 field_name 排序
    latest_docs = list(collection.find({"board":board}).sort(field_name, -1).limit(limit))

    # 確保資料集不為空
    if latest_docs:
        # 取得第 limit 筆（最舊的那筆資料）的 field 值
        oldest_value = latest_docs[-1][field_name]

        # 刪除所有比這個 field 值還要舊的資料
        result = collection.delete_many({
            field_name: {'$lt': oldest_value}
        })

        print(f"Deleted {result.deleted_count} documents.")
    else:
        print("No documents found.")
