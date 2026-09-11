from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.chat_home, name='home'),
    path('new/', views.new_conversation, name='new'),
    path('chat/<int:conv_id>/', views.chat, name='chat'),
    path('chat/<int:conv_id>/send/', views.send_message, name='send'),
]
