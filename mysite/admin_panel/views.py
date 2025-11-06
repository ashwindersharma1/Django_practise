from django.shortcuts import render
from accounts.utils import admin_required
from admin_panel.models import RadioStation,Market,Format,Representative
from django.core.paginator import Paginator
# Create your views here.

@admin_required
def dashboard(request):
    return render(request, 'admin_panel/dashboard.html')

def view_campaigns(request):
    return render(request, 'admin_panel/view_campaigns.html')

def view_radio_stations(request):
     radio_stations = (
        RadioStation.objects
        .select_related('market', 'format', 'rep')
        .all()
        .order_by('name')
    )

def list_radio_stations(request):
    # Base queryset with joins
    radio_stations_qs = (
        RadioStation.objects
        .select_related('market', 'format', 'rep')
        .all()
        .order_by('name')
    )

    # --- Pagination setup ---
    page_number = request.GET.get('page', 1)
    paginator = Paginator(radio_stations_qs, 10)  # 10 records per page
    page_obj = paginator.get_page(page_number)

    # --- Counts ---
    total_stations = RadioStation.objects.count()
    active_stations = RadioStation.objects.filter(is_active=True).count()
    total_markets = Market.objects.count()

    context = {
        'page_obj': page_obj,
        'total_stations': total_stations,
        'active_stations': active_stations,
        'total_markets': total_markets,
    }

    return render(request, 'admin_panel/layout/radio_stations/list.html', context)