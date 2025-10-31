from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('home/', views.user_dashboard, name='user_dashboard'),
    path('logout/', views.user_logout, name='logout'),
]
