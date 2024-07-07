from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
load_dotenv()

# MongoDB connection details
connection_string = os.getenv('MONGODB_CONN_STRING')
database_name = os.getenv('DB_NAME')
client = MongoClient(connection_string)
db = client[database_name]
chat_collection = os.getenv('USERCHAT_COLLECTION_NAME')

def insert_chat_document(user_id, chat_name):
    """
    Inserts a new chat document.
    """
    document = {
        'user_id': user_id,
        'chat_name': chat_name,
        'chat_doc_ids': [],
        'chat_urls_id_array': []
    }
    return chat_collection.insert_one(document).inserted_id

def insert_chat_doc_id(chat_id, doc_id):
    """
    Inserts a document ID into the chat_doc_ids array of an existing chat document.
    """
    return chat_collection.update_one(
        {'_id': ObjectId(chat_id)},
        {'$addToSet': {'chat_doc_ids': doc_id}}
    )

def delete_chat_doc_id(chat_id, doc_id):
    """
    Deletes a document ID from the chat_doc_ids array of an existing chat document.
    """
    return chat_collection.update_one(
        {'_id': ObjectId(chat_id)},
        {'$pull': {'chat_doc_ids': doc_id}}
    )

def insert_chat_url_id(chat_id, url_id):
    """
    Inserts a URL ID into the chat_urls_id_array of an existing chat document.
    """
    return chat_collection.update_one(
        {'_id': ObjectId(chat_id)},
        {'$addToSet': {'chat_urls_id_array': url_id}}
    )

def delete_chat_url_id(chat_id, url_id):
    """
    Deletes a URL ID from the chat_urls_id_array of an existing chat document.
    """
    return chat_collection.update_one(
        {'_id': ObjectId(chat_id)},
        {'$pull': {'chat_urls_id_array': url_id}}
    )

def update_chat_name(chat_id, new_chat_name):
    """
    Updates the chat_name of an existing chat document.
    """
    return chat_collection.update_one(
        {'_id': ObjectId(chat_id)},
        {'$set': {'chat_name': new_chat_name}}
    )