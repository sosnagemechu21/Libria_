from django.urls import path
from . import views

app_name = 'study'

urlpatterns = [
    path('', views.study_setup, name='setup'),
    path('session/<int:session_id>/', views.study_session, name='session'),
    path('session/<int:session_id>/update/', views.update_session, name='update_session'),
    path('session/<int:session_id>/break/', views.take_break, name='take_break'),
    path('break/<int:break_id>/', views.break_screen, name='break_screen'),
    path('break/<int:break_id>/end/', views.end_break, name='end_break'),
    path('complete/<int:session_id>/', views.session_complete, name='complete'),
    path('youtube/search/', views.youtube_search, name='youtube_search'),
    
    # Focus Loop Boundary Engine API
    path('api/events/log/', views.api_events_log, name='api_events_log'),
    path('api/status/', views.api_status, name='api_status'),
]
