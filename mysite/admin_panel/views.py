from django.shortcuts import render
from accounts.utils import admin_required

# Create your views here.

@admin_required
def dashboard(request):
    return render(request, 'admin_panel/dashboard.html')

def view_campaigns(request):
    return render(request, 'admin_panel/view_campaigns.html')