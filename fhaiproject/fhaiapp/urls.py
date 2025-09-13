from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    #path('details', views.details, name='details'),
    #path('farha-ai', views.farha_ai_engine_chat, name='farha-ai'),
]