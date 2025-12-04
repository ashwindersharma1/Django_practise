from django.shortcuts import render, redirect
from accounts.utils import admin_required
from django.contrib import messages
# from django.db.models import Q,Count,Case,When
from django.db.models import Count, Case, When, Value, CharField
from datetime import datetime, timedelta, date
from accounts.models import User
from pprint import pprint
import math
from django.db.models import Q

# from django.db.models import Count

from admin_panel.models import RadioStation, Market, Format, Representative, User, Campaign, Schedule
from django.core.paginator import Paginator
# Create your views here.

@admin_required
def dashboard(request):
    return render(request, 'admin_panel/dashboard.html')

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
        'formats': Format.objects.all(),
        'reps': Representative.objects.all(),
        'users': User.objects.all(),
        'station': {
            # 'station': page_obj.stations,   # no specific station selected
            'markets': Market.objects.all(),
            'formats': Format.objects.all(),
            'rep': Representative.objects.all(),
            'users': User.objects.all(),
        },
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
    
    context = {
        'station': station,
        'markets': Market.objects.all(),
        'formats': Format.objects.all(),
        'rep': Representative.objects.all(),
        'users': User.objects.all(),
    }    
    return render(request, 'admin_panel/layout/radio_stations/view_radio_station.html', {'station': context})


# def edit_radio_station(request, slug):
#     station = get_object_or_404(
#         RadioStation.objects.select_related('market', 'format', 'rep'),
#         slug=slug
#         )
#     return render(request, 'admin_panel/layout/radio_stations/edit_radio_station.html', {'station': station})

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import RadioStation, Market, Format, Representative, User

@require_POST
def update_station(request, slug):
    try:
        station = get_object_or_404(RadioStation, slug=slug)

        # --- Update simple fields ---
        station.name = request.POST.get('name', station.name)
        station.owner = request.POST.get('owner', station.owner)
        station.station_group = request.POST.get('station_group')
        station.description = request.POST.get('description', station.description)

        # --- Update foreign keys (check if provided) ---
        market_id = request.POST.get('market')
        format_id = request.POST.get('format')
        rep_id = request.POST.get('rep')
        assign_user_id = request.POST.get('assign_user')

        if market_id:
            station.market_id = market_id
        if format_id:
            station.format_id = format_id
        if rep_id:
            station.rep_id = rep_id
        if assign_user_id:
            station.assign_user_id = assign_user_id

        # --- Save changes ---
        station.save()
        messages.success(request, f"Station '{station.name}' updated successfully!")
        return JsonResponse({"success": True, "message": "Station updated successfully!"})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


def delete_radio_station(request, slug):
    station = get_object_or_404(RadioStation, slug=slug)
    # station.delete()
    # messages.success(request, f"Station '{station.name}' deleted successfully!")
    # return redirect('list_radio_stations') 
    # return JsonResponse({"success": True, "message": "Station deleted successfully!"})
    
    try:
        station_name = station.name  # store before delete
        deleted_count, _ = station.delete()  # returns (num_deleted, details)

        if deleted_count > 0:
            messages.success(request, f"Station '{station_name}' deleted successfully!")
            return redirect('list_radio_stations')
        else:
            messages.warning(request, f"⚠️ Station '{station_name}' could not be deleted.")
            return redirect(request.META.get('HTTP_REFERER', 'list_radio_stations'))

    except Exception as e:
        messages.error(request, f"❌ Failed to delete station: {e}")
        return redirect(request.META.get('HTTP_REFERER', 'list_radio_stations'))


def list_campaigns(request):

    total_campaigns = Campaign.objects.count()
    total_schedules = Schedule.objects.count()
    in_progress = Schedule.objects.filter(schedule_status='Pending Review (Admin)').count()
    submitted = Schedule.objects.filter(schedule_status='Submitted').count()
    # campaigns_list = Campaign.objects.annotate(
    #     schedule_count=Count('schedules'),
    #     campaign_status=Case(
    #             When(end_date__lt=date.today(), then=Value("Expired")),
    #             When(end_date__gte=date.today(), then=Value("Active")),
    #             default=Value("Unknown"),
    #             output_field=CharField()
    #         )
    #     ).order_by('-updated_at')

    
    campaigns_list = (Campaign.objects
    .prefetch_related('schedules')              # for M2M join
                        .annotate(
                            schedule_count=Count('schedules', distinct=True),
                            campaign_status=Case(
                                When(end_date__lt=date.today(), then=Value("Expired")),
                                When(end_date__gte=date.today(), then=Value("Active")),
                                default=Value("Unknown"),
                                output_field=CharField()
                            )
                        ).order_by('-updated_at'))
    

    query = request.GET.get('q', '').strip()
    # status_filter = request.GET.get('status', '')

    # Base queryset with joins
    # radio_stations_qs = (
    #     RadioStation.objects
    #     .select_related('market', 'format', 'rep')
    #     .all()
    #     .order_by('name')
    # )

      # --- Filtering logic ---
    if query:
        campaigns_list = campaigns_list.filter(
            Q(name__icontains=query)
        )

    # --- Pagination setup ---
    page_number = request.GET.get('page', 1)
    paginator = Paginator(campaigns_list, 10)  # 10 records per page
    page_obj = paginator.get_page(page_number)

  # --- Stats ---

    context = {
        'page_obj': page_obj,
        'query': query,
        # 'station': {
        #     # 'station': page_obj.stations,   # no specific station selected
        #     'markets': Market.objects.all(),
        #     'formats': Format.objects.all(),
        #     'rep': Representative.objects.all(),
        #     'users': User.objects.all(),
        # },
    }

 # If HTMX or AJAX request, return partial
    if request.headers.get('HX-Request') == 'true' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/layout/radio_stations/station_list_partial.html', context)

    # return render(request, 'admin_panel/layout/campaigns/listing.html', context)    
    
    return render(request, 'admin_panel/layout/campaigns/lisitng.html', {
        'page_obj': page_obj,
        'total_campaigns': total_campaigns,
        'total_schedules': total_schedules,
        'in_progress': in_progress,
        'submitted': submitted,
        'campaigns_list': campaigns_list,
        'today': date.today(),
    })


def edit_campaign(request,slug):
    campaign = get_object_or_404(Campaign, slug=slug)
    return render(request, 'admin_panel/layout/campaigns/edit_campaign.html', {'campaign': campaign})


# def update_campaign(request,slug):
#     campaign.save()
#     return render(request, 'admin_panel/layout/campaigns/edit_campaign.html', {'campaign': campaign})


# @require_POST
def update_campaign(request, slug):
    campaign = get_object_or_404(Campaign, slug=slug)

    if request.method == "POST":
       
        # if request.method == "POST":

        campaign.name = request.POST.get("name", campaign.name)

        # Fix 1: Correct name is `date_mode`
        date_mode = request.POST.get("date_mode")

        # --- Start Date ---
        start_date_str = request.POST.get("start_date")
        if start_date_str:
            campaign.start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()

        # --- Manual Mode ---
        if date_mode == "manual":
            end_date_str = request.POST.get("end_date")
            if end_date_str:
                campaign.end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            # Manual mode means weeks = calculated
            diff = (campaign.end_date - campaign.start_date).days
            campaign.weeks = math.ceil(diff / 7)

        # --- Broadcast Weeks Mode ---
        elif date_mode == "weeks":

            # Fix 2: Correct field name is `weeks`
            weeks = int(request.POST.get("weeks", 0))

            if weeks > 0:
                campaign.weeks = weeks
                campaign.end_date = campaign.start_date + timedelta(weeks=weeks)

        campaign.save()

        messages.success(request, "Campaign updated successfully!")
        return redirect("edit_campaign", slug=campaign.slug)

    # context = {"campaign": campaign}
    return render(request, 'admin_panel/layout/campaigns/edit_campaign.html', {'campaign': campaign})
    # return render(request, "admin_panel/campaign/edit_campaign.html", context)
    

def view_campaign(request,slug):
    campaign = get_object_or_404(Campaign, slug=slug)
    schedules = campaign.schedules.all().order_by('-created_at')
    # pprint(list(schedules.values()))
    
  

    search_query = request.GET.get('search', '').strip()

    if search_query:
        schedules = schedules.filter(
            Q(name__icontains=search_query) |
            Q(schedule_status__icontains=search_query)
        )

      # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(schedules, 5)     # 5 schedules per page
    page_obj = paginator.get_page(page_number)
    context = {
        'campaign': campaign,
        'page_obj': page_obj,
    }    
    # schedules = schedules.filter(name__icontains=query)
    # HTMX request → send partial HTML
    if request.headers.get('HX-Request') == 'true':
       return render(request, 'admin_panel/layout/campaigns/view_campaign_partial.html', context)

    return render(request, 'admin_panel/layout/campaigns/view_campaign.html', context)
    