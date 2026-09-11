from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.library_home, name='home'),
    path('grade/<int:grade_number>/', views.grade_detail, name='grade'),
    path('grade/<int:grade_number>/<slug:subject_slug>/', views.subject_textbooks, name='subject'),
    path('textbook/<int:textbook_id>/', views.textbook_detail, name='textbook'),
]
