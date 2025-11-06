from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    path('campaigns/', views.view_campaigns, name='view_campaigns'),
     path('radio_stations/', views.list_radio_stations, name='list_radio_stations')
]
