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
]