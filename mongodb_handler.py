from datetime import datetime
from pymongo import MongoClient
import pt_config
import pt_logger
from pprint import pprint

logger = pt_logger.logger

class MongoDBHandler:
    def __init__(self, db_name='website', collection_name='pirate'):
        self.client = MongoClient(pt_config.DB_SERVER)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_to_database(self, chat_id=None, board=None, title=None, link=None, author=None):
        current_time = datetime.now()
        if not title:
            logger.info("Title is none or empty, no insert performed.")
            return False, current_time

        product_details = {
            'author': author,
            'board': board.strip(),
            'title': title.strip(),
            'link': link,
            'insert_time': current_time,
            'chat_id': chat_id,
            'tg_notify_time': None,
            'gmail_notify_time': None,
            'pttmail_notify_time': None
        }

        try:
            existing_document = self.collection.find_one({
                'board': product_details['board'],
                'title': product_details['title'],
                'link': product_details['link']
            })

            if existing_document is None:
                result = self.collection.insert_one(product_details)
                logger.info(f"Inserted new document with id: {result.inserted_id}")
                return True, product_details, current_time
            else:
                logger.info("Duplicate document found, no insert performed.")
                return False, current_time
        except Exception as e:
            logger.error(f"Error inserting document: {e}")
            return False, current_time

    def retrieve_updates_after_time_allow_deny(self, type, allow_keywords, deny_keywords):
        try:
            query = {
                type: None,
                "board": {"$in": [pt_config.TERM_PTT_BOARD]},
                "$and": [
                    {"title": {"$regex": allow_keywords, "$options": "i"}},
                    {"title": {"$not": {"$regex": deny_keywords, "$options": "i"}}}
                ]
            }
            documents = self.collection.find(query).limit(1)
            pprint(query)
            json_array = [doc for doc in documents]
            logger.info(f"Retrieved {len(json_array)} documents for notification.")
            return json_array
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

    def retrieve_updates_after_time_keywords(self, type, keywords):
        try:
            documents = self.collection.find({
                type: None,
                "board": {"$in": [pt_config.TERM_PTT_BOARD]},
                "$or": [{"title": {"$regex": keyword, "$options": "i"}} for keyword in keywords]
            }).limit(1)
            json_array = [doc for doc in documents]
            logger.info(f"Retrieved {len(json_array)} documents for notification.")
            return json_array
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

    def retrieve_updates_after_time(self, type, board_only):
        try:
            documents = self.collection.find({
                type: None,
                "board": {"$in": board_only}
            }).limit(pt_config.TELEGRAM_NOTIFY_ONCE_COUNT)
            json_array = [doc for doc in documents]
            logger.info(f"Retrieved {len(json_array)} documents for notification.")
            return json_array
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

    def update_notify_time(self, type, _id):
        current_time = datetime.now()
        try:
            result = self.collection.update_one(
                {'_id': _id},
                {'$set': {type: current_time}}
            )
            if result.modified_count > 0:
                logger.info(f"Document with _id {_id} was updated successfully.")
            else:
                logger.warning(f"No changes made to the document with _id {_id}.")
        except Exception as e:
            logger.error(f"Error updating document with _id {_id}: {e}")

    def delete_old_documents(self, board='Gossiping', limit=20):
        field_name = '_id'
        try:
            latest_docs = list(self.collection.find({"board": board}).sort(field_name, -1).limit(limit))
            if latest_docs:
                oldest_value = latest_docs[-1][field_name]
                result = self.collection.delete_many({
                    field_name: {'$lt': oldest_value}
                })
                logger.info(f"Deleted {result.deleted_count} documents.")
            else:
                logger.info("No documents found to delete.")
        except Exception as e:
            logger.error(f"Error deleting old documents: {e}")
