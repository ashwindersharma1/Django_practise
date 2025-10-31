from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from accounts.models import User
from .utils import admin_required, user_required
from django.contrib.auth.hashers import make_password

# Create your views here.
def home(request):
    return HttpResponse("Hello, Django from scratch!")

def login_view(request):

    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')

    if user_id and user_role:
        if user_role == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('user_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)  # pylint: disable=no-member
            print(f"DEBUG: role = '{user.role}'")
            if check_password(password, user.password):  # plain-text check for now
                # TODO: replace with hashing later
                request.session['user_id'] = str(user.id)
                request.session['user_role'] = user.role
                messages.success(request, f'Welcome {user.name or user.email}!')
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('user_dashboard')
            else:
                messages.error(request, 'Invalid password.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')

    return render(request, 'login.html')

@admin_required
def admin_dashboard(request):
     return render(request, 'admin/dashboard.html')
    # return HttpResponse("Welcome to Admin Dashboard")

@user_required
def user_dashboard(request):
     return render(request, 'user/dashboard.html')
    # return HttpResponse("Welcome to User Home")    


def user_logout(request):
    request.session.flush()
    return redirect('login')    