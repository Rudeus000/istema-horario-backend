"""
URLs para el chatbot
"""
from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('help/', views.help, name='help'),
]

