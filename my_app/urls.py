from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('put/', views.add_item, name='put'),
    path('get/', views.get_item, name='get'),
    path('delete/', views.delete_item, name='delete'),
    path('clear/', views.clear_cache, name='clear'),
    path('all/', views.get_all_items, name='all'),
    path('logs/', views.view_logs, name='logs'),
]