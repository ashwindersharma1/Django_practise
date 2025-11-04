from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('home/', views.user_dashboard, name='user_dashboard'),
    path('logout/', views.user_logout, name='logout'),
]
