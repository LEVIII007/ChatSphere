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
load_dotenv()
import io

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


# @api_view(['POST'])
# def upload_file(request):
#     user = request.data.get('user')
#     chat_name = request.data.get('chat_name')
#     if request.method == 'POST' and request.FILES.get('file'):
#         uploaded_file = request.FILES['file']
#         file_name = default_storage.save(uploaded_file.name, uploaded_file)
#         vectorize.save_pdf_embeddings_to_database(file_name, chat_name, user)
#         return JsonResponse({'status': 'success', 'file_name': file_name})
#     return JsonResponse({'status': 'please upload a valid pdf file'}, status=400)

@api_view(['POST'])
def upload_file(request):
    user = request.data.get('user')
    chat_name = request.data.get('chat_name')
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        # Read the uploaded file's content into memory
        file_content = uploaded_file.read()
        # Pass the file content directly to the vectorize function
        vectorize.save_pdf_embeddings_to_database(file_content, chat_name, user)
        return JsonResponse({'status': 'success', 'file_name': uploaded_file.name})
    return JsonResponse({'status': 'please upload a valid pdf file'}, status=400)

@api_view(['POST'])
def url_embeddings(request):
    url = request.data.get('url')
    user = request.data.get('user')
    chat_name = request.data.get('chat_name')
    vectorize.save_url_embeddings_to_database(url, user, chat_name)
    return Response({'status': 'success'})


@api_view(['GET'])
def test_token(request):
    return Response({})





