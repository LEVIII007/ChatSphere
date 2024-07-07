from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
load_dotenv()

connection_string = os.getenv('MONGODB_CONN_STRING')
database_name = os.getenv('DB_NAME')
client = MongoClient(connection_string)
db = client[database_name]

# Correctly initialize collections
chat_collection = db[os.getenv('USERCHAT_COLLECTION_NAME')]
embeddings_collection = db[os.getenv('EMB_COLLECTION_NAME')]
messages_collection = db[os.getenv('CHAT_COLLECTION_NAME')]


def insert_chat_document(user_id, chat_name):
    """
    Inserts a new chat document.
    """
    document = {
        'user_id': user_id,
        'chat_name': chat_name,
        'documents': [],
    }
    return chat_collection.insert_one(document).inserted_id



def insert_chat_doc(chat_id, doc_name):
    """
    Inserts a document ID into the chat_doc_ids array of an existing chat document.
    """
    doc_id = ObjectId()
    chat_doc = {
        'doc_id': doc_id,
        'doc_name': doc_name,
    }
    result = chat_collection.update_one(
        {'_id': ObjectId(chat_id)},
        {'$push': {'documents': chat_doc}}
    )
    if result.modified_count == 1:
        return doc_id
    else:
        return None




def delete_chat_doc(chat_id, doc_name):
    """
    Deletes a document by doc_name from the documents array of an existing chat document,
    and also deletes all embedding documents related to that document from the embeddings collection.
    """
    # Step 1: Find the document in the chat document to get its doc_id
    chat_doc = chat_collection.find_one({'_id': ObjectId(chat_id), 'documents.doc_name': doc_name}, {'documents.$': 1})
    if not chat_doc or 'documents' not in chat_doc or len(chat_doc['documents']) == 0:
        return None  # Document not found

    doc_id = chat_doc["documents"][0]['doc_id']

    # Step 2: Delete the document from the chat document's documents array
    chat_collection.update_one(
        {'_id': ObjectId(chat_id)},
        {'$pull': {'documents': {'doc_id': doc_id}}}
    )
    
    # Step 3: Delete all embedding documents related to that doc_id from the embeddings collection
    embeddings_collection.delete_many({'doc_id': doc_id})
    
    return doc_id  # Return the doc_id of the deleted document




def update_chat_name(chat_id, new_chat_name):
    """
    Updates the chat_name of an existing chat document.
    """
    return chat_collection.update_one(
        {'_id': ObjectId(chat_id)},
        {'$set': {'chat_name': new_chat_name}}
    )



def delete_related_embeddings(doc_ids):
    """
    Deletes all embedding documents related to the given doc_ids.
    """
    embeddings_collection.delete_many({'doc_id': {'$in': doc_ids}})



def delete_chat(chat_id):
    """
    Deletes a chat document and all related chat_docs and embedding documents.
    """
    # Convert chat_id to ObjectId if it's not already one
    chat_id = ObjectId(chat_id) if not isinstance(chat_id, ObjectId) else chat_id
    
    # Find the chat document to get all doc_ids in its documents array
    chat_document = chat_collection.find_one({'_id': chat_id}, {'documents.doc_id': 1})
    if chat_document and 'documents' in chat_document:
        doc_ids = [doc['doc_id'] for doc in chat_document['documents']]
        
        # Delete related embedding documents
        delete_related_embeddings(doc_ids)
    
    # Finally, delete the chat document itself
    chat_collection.delete_one({'_id': chat_id})

# insert_chat_document('60b9b3b3bb3b3b3b3b3b3sev', 'Test2 Chat')
# insert_chat_document('60b9b3b3bb3b3b3b3b3bgesb3', 'Test3 Chat')
# insert_chat_document('60b9b3b3bb3b3b3bsve3b3b3', 'Test3 Chat')


delete_chat_doc('668a9905e5f9556543d65b87', 'Test Doc 5')
# insert_chat_doc('668a9905e5f9556543d65b87', 'Test Doc 5')
# insert_chat_doc('668a9905e5f9556543d65b87', 'Test Doc 3')
# insert_chat_doc('668a9905e5f9556543d65b87', 'Test Doc 4')









# user deletion not needed 
# chat deletion  : chat deletion, emb deletion. 

# doc deletion : doc deletion, emb deletion.
