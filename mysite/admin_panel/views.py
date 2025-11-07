from django.shortcuts import render
from accounts.utils import admin_required
from django.db.models import Q
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
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')

    # Base queryset with joins
    radio_stations_qs = (
        RadioStation.objects
        .select_related('market', 'format', 'rep')
        .all()
        .order_by('name')
    )

      # --- Filtering logic ---
    if query:
        radio_stations_qs = radio_stations_qs.filter(
            Q(name__icontains=query)
            | Q(owner__icontains=query)
            | Q(market__name__icontains=query)
        )

    if status_filter == 'active':
        radio_stations_qs = radio_stations_qs.filter(is_active=True)
    elif status_filter == 'inactive':
        radio_stations_qs = radio_stations_qs.filter(is_active=False)


    # --- Pagination setup ---
    page_number = request.GET.get('page', 1)
    paginator = Paginator(radio_stations_qs, 10)  # 10 records per page
    page_obj = paginator.get_page(page_number)

  # --- Stats ---
    total_stations = RadioStation.objects.count()
    active_stations = RadioStation.objects.filter(is_active=True).count()
    total_markets = Market.objects.count()

    context = {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'total_stations': total_stations,
        'active_stations': active_stations,
        'total_markets': total_markets,
    }

 # If HTMX or AJAX request, return partial
    if request.headers.get('HX-Request') == 'true' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/layout/radio_stations/station_list_partial.html', context)

    return render(request, 'admin_panel/layout/radio_stations/list.html', context)
   

from django.shortcuts import get_object_or_404
def view_radio_station(request, slug):
    station = get_object_or_404(
        RadioStation.objects.select_related('market', 'format', 'rep'),
        slug=slug
        )
    return render(request, 'admin_panel/layout/radio_stations/view_radio_station.html', {'station': station})