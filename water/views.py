from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import user_passes_test
from .forms import AdminApprovalForm
from .models import WaterStation
from django.views import generic
from django.conf import settings
from .models import *
from .forms import *
from django.urls import reverse

# REFERENCE: https://medium.com/djangotube/django-roles-groups-and-permissions-introduction-a54d1070544
# REFERENCE: https://developers.google.com/maps/documentation/javascript/examples/event-simple

def is_admin(user):
    return user.is_authenticated and user.groups.filter(name='admin').exists()

def is_base(user):
    return user.is_authenticated and not user.groups.filter(name='admin').exists()

def is_logged_in(user):
    return user.is_authenticated

def map(request):
    key = settings.GOOGLE_API_KEY
    buildings = Building.objects.all()
    context = {
        'key': key,
        'buildings': buildings,
        'title': 'Map',
        'admin': is_admin(request.user),
    }
    return render(request, 'map.html', context)

class MapStationsView(generic.ListView):
    def get(self, request, place_id):
        stations = WaterStation.objects.filter(approved=True, building__place_id = place_id).order_by('floor')
        floors = WaterStation.objects.filter(approved=True, building__place_id = place_id).values('floor').distinct().order_by('floor')
        context = {
            'stations': stations,
            'floors': floors,
        }
        return render(request, 'map_stations.html', context)


def home(request):
    return render(request, 'home.html', { 'title': 'Home', 'admin': is_admin(request.user) })

def login(request):
    if not request.user.is_authenticated:
        return render(request, 'login.html', { 'title': 'Login' })
    else:
        # redirect logged-in user to home
        return redirect('/')

def logout(request):
    # call default logout for functionality
    auth_logout(request)
    # redirect logged-out user to home
    return redirect('/')

@user_passes_test(is_logged_in, login_url='error')
def submit_water_station(request):
    user_water_stations = WaterStation.objects.filter(user=request.user)
    key = settings.GOOGLE_API_KEY
    if request.method == 'POST':
        form = WaterStationForm(request.POST)
        if form.is_valid():
            water_station = form.save(commit=False)
            water_station.user = request.user
            if is_admin(request.user):
                water_station.approved = True  # Set approval status as True for admins
            else:
                water_station.approved = False  # Set approval status as False by default
            water_station.save()
            return redirect('submit_water_station')  # Redirect to the home page after submission
    else:
        form = WaterStationForm()
    context = {
        'form': form ,
        'key': key,
        'title': 'New Water Station',
        'admin': is_admin(request.user),
        'user_water_stations': user_water_stations,
    }
    return render(request, 'submit_water_station.html', context)


@user_passes_test(is_admin, login_url='error')
def approve_water_station(request):
    # filter not working on sqlite (boolean), OK on postgres so leave as is
    unapproved_water_stations = WaterStation.objects.filter(approved=False)

    if request.method == 'POST':
        admin_form = AdminApprovalForm(request.POST)  # Use the custom admin approval form
        if admin_form.is_valid():
            for water_station in unapproved_water_stations:
                approval_status = request.POST.get('radio-group-' + str(water_station.id))
                print(approval_status)
                if approval_status == 'approved':
                    water_station.approved = True
                    water_station.save()
                elif approval_status == 'rejected':
                    water_station.delete()
            return redirect('approve_water_station')
    else:
        admin_form = AdminApprovalForm()  # Use the custom admin approval form
        context = {
            'admin_form': admin_form,
            'unapproved_water_stations': unapproved_water_stations,
            'admin': is_admin(request.user),
            'title': 'Approve Water Stations',
        }
        return render(request, 'approve_water_station.html', context)

@user_passes_test(is_base, login_url='error')
def user_water_stations(request):
    user_water_stations = WaterStation.objects.filter(user=request.user)
    context = {
        'user_water_stations': user_water_stations,
        'title': 'Your Water Stations',
    }
    return render(request,'user_water_stations.html', context)

def error(request):
    return render(request, 'error.html', {'title':'Page not found'})