"""
URLs do app desafios
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('analyze/', views.analyze_challenge, name='analyze_challenge'),
    path('analyses/', views.list_analyses, name='list_analyses'),
    path('analyses/<int:analysis_id>/', views.get_analysis, name='get_analysis'),
    path('analysis/<int:analysis_id>/', views.analysis_detail, name='analysis_detail'),
    path('challenges/', views.challenge_list, name='challenge_list'),
    path('challenge/<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('search/', views.search, name='search'),
    path('health/', views.health_check, name='health_check'),
]
