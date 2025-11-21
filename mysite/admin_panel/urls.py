from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    path('radio_stations/', views.list_radio_stations, name='list_radio_stations'),
    path('station/<slug:slug>', views.view_radio_station, name='view_radio_station'),
    path('update-station/<slug:slug>', views.update_station, name='edit_radio_station'),
    path('delete-station/<slug:slug>', views.delete_radio_station, name='delete_radio_station'),
    # campaigns
    path('campaigns/', views.list_campaigns, name='campaigns_listing')
    
]
