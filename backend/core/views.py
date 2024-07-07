# from .models import *
# from .serializer import *
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from .serializer import UserSerializer
# from django.contrib.auth.models import User
# from rest_framework import status




# @api_fiew(['POST'])
# def login(request):
#     user = get_object_or_404(User, username=request.data['username'])
#     if not user.check_password(request.data['password']):
#         return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
#     token = Token.objects.get_or_create(user=user)
#     serializer = UserSerializer(instance = user)
#     return Response({'token' : token.key, 'user': serializer.data})



# @api_fiew(['POST'])
# def signup(request):
#     serializer = UserSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()       #saving in db
#         user = User.objects.get(username=serializer.data['username'])
#         user.set_password(request.data['password'])  #hashing the password
#         user.save()
#         token = Token.objects.create(user=user)
#         return Response({'token': token.key, 'user': serializer.data})
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from dotenv import load_dotenv
import os
from gpt import vectorize
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
load_dotenv()
import io
import json
# MongoDB connection setup
mongo_url = os.getenv('MONGODB_CONN_STRING')
client = MongoClient(mongo_url)
db = client['GPT']
users_collection = db['users']

def hash_password(password):
    # Hash a password for the first time
    # Using bcrypt, the salt is saved into the hash itself
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(hashed_password, user_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)

def generate_token():
    # Simplified token generation; consider using a more secure method
    return str(ObjectId())

@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    # Check if username already exists
    if users_collection.find_one({"username": username}):
        return Response({'detail': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Hash the password and create user
    hashed_password = hash_password(password)
    user_id = users_collection.insert_one({
        "username": username,
        "password": hashed_password,
    }).inserted_id
    
    # Generate token
    token = generate_token()
    users_collection.update_one({"_id": user_id}, {"$set": {"token": token}})
    print("signup done!")
    
    return Response({'token': token, 'user': {'username': username}})

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = users_collection.find_one({"username": username})
    if not user or not check_password(user['password'], password):
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Ensure token exists
    if 'token' not in user:
        token = generate_token()
        users_collection.update_one({"_id": user['_id']}, {"$set": {"token": token}})
    else:
        token = user['token']
    print("login done!")
    
    return Response({'token': token, 'user': {'username': username}})


@api_view(['POST'])
def upload_file(request):
    user_id = request.data.get('user_id')
    chat_id = request.data.get('chat_id')

    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        doc_id = insert_chat_doc(chat_id, uploaded_file.name)
        if doc_id is None:
            return Response({'status': 'error', 'message': 'Failed to insert document'}, status=500)
        else
            # Read the uploaded file's content into memory
            file_content = uploaded_file.read()
            # Pass the file content directly to the vectorize function
            vectorize.save_pdf_embeddings_to_database(file_content, chat_name, user)
            return JsonResponse({'status': 'success', 'file_name': uploaded_file.name})
        return JsonResponse({'status': 'please upload a valid pdf file'}, status=400)

@api_view(['POST'])
def url_embeddings(request):
    url = request.data.get('url')
    user = request.data.get('user_id')
    chat_name = request.data.get('chat_id')
    doc_id = insert_chat_doc(chat_id, url)
    if doc_id is None:
        return Response({'status': 'error', 'message': 'Failed to insert document'}, status=500)
    else:
        vectorize.save_url_embeddings_to_database(url, user, chat_name)
        return Response({'status': 'success'})


@api_view(['GET'])
def test_token(request):
    return Response({})


@api_view(['POST'])
def send_past_messages(request):
    session = request.data.get("session_id")
    connection_string = os.getenv("MONGODB_CONN_STRING")
    database_name = os.getenv("DB_NAME")
    collection_name = os.getenv("CHAT_COLLECTION_NAME")

    # Establish a connection to MongoDB
    client = MongoClient(connection_string)

    # Access the specific database and collection
    db = client[database_name]
    collection = db[collection_name]

    # Query the collection for documents with the specified session_id
    messages = collection.find({"SessionId": session})

    human_messages = []
    ai_messages = []
    for message in messages:
        # Parse the History field from string to dictionary
        history = json.loads(message['History'])
        
        # Extract type and content
        msg_type = history.get("type")
        content = history.get("data", {}).get("content", "")
        
        # Save messages based on their type
        if msg_type == "human":
            human_messages.append(content)
        elif msg_type == "ai":
            ai_messages.append(content)

    return Response({"human_messages": human_messages, "ai_messages": ai_messages})


@api_view(['POST'])
def user_chats(request):
    session = request.data.get("user_id")
    connection_string = os.getenv("MONGODB_CONN_STRING")
    database_name = os.getenv("DB_NAME")
    collection_name = os.getenv("CHAT_COLLECTION_NAME")


@api_view(['POST'])
def chat_ops(request):
    try:
        data = json.loads(request.body)
        function = data.get('function')
        
        # For operations other than creating a new chat, expect a chat_id
        if function != 'insert_chat_document':
            chat_id = data.get('chat_id')
            # Ensure chat_id is in a proper format for MongoDB operations
            if chat_id:
                chat_id = str(ObjectId(chat_id))
            else:
                return JsonResponse({'status': 'error', 'message': 'chat_id is required for this operation'}, status=400)
        else:
            chat_id = None

        if function == 'insert_chat_document':
            user_id = data.get('user_id')
            chat_name = data.get('chat_name')
            result_id = insert_chat_document(user_id, chat_name)
            return JsonResponse({'status': 'success', 'chat_id': str(result_id)})
        
        elif function == 'insert_chat_doc':
            doc = data.get('doc')
            chat_id = data.get('chat_id')
            doc_id = insert_chat_doc_id(chat_id, doc)
            return JsonResponse({'status': 'success', 'doc_id': str(doc_id)})
        
        elif function == 'delete_chat_doc':
            doc = data.get('doc')
            chat_id = data.get('chat_id')
            doc_id = delete_chat_doc_id(chat_id, doc)
            return JsonResponse({'status': 'success', 'doc_id': str(doc_id)})
        
        elif function == 'delete_chat':
            url_id = data.get('url_id')
            delete_chat(chat_id)
        
        elif function == 'update_chat_name':
            new_chat_name = data.get('new_chat_name')
            update_chat_name(chat_id, new_chat_name)
        
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid function specified'}, status=400)
        
        return JsonResponse({'status': 'success', 'chat_id': chat_id})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



@csrf_exempt
@require_http_methods(["POST"])
def get_chat_names(request):
    try:
        # Load JSON data from the request
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'user_id is required'}, status=400)
        
        # MongoDB connection details
        connection_string = os.getenv('MONGODB_CONN_STRING')
        database_name = os.getenv('DB_NAME')
        client = MongoClient(connection_string)
        db = client[database_name]
        chat_collection = os.getenv('USERCHAT_COLLECTION_NAME')
        
        # Query to find all chats for the given user_id
        chats = chat_collection.find({'user_id': user_id}, {'chat_name': 1})
        
        # Extract chat names from the query result
        chat_names = [chat['chat_name'] for chat in chats]
        
        return JsonResponse({'status': 'success', 'chat_names': chat_names})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)







# user :
# email, username, picture, user_id

# create a new user:
# delete a user:
# update a user:

# chat:
# chat_id, user_id, chat_name, chat_documents, chat_urls.

# create a new chat:
# delete a chat:
# update a chat: delete docs, delete urls, change name


# chat_messages:

# chat_id, chat_history














