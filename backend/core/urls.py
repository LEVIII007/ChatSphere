from django.contrib import admin
from django.urls import re_path
from . import views
# from views import *


urlpatterns = [
    re_path('login', views.login),
    re_path('signup', views.signup),
    re_path('test_token', views.test_token),
    re_path('upload_file', views.upload_file),
    re_path('url_embeddings', views.url_embeddings),
    re_path('past_messages', views.send_past_messages),
    re_path("user_chats", views.chat_ops),
    re_path("chat_messages", views.get_chat_names),
]