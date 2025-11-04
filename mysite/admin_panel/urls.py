from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    path('campaigns/', views.view_campaigns, name='view_campaigns'),
]
