from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
import requests
from .models import Driver

"""
API documentation
https://openf1.org/
https://github.com/br-g/openf1

for driver in f1_data_drivers: #populate database with drivers info
    Driver.objects.create(
        first_name = driver['first_name'],
        last_name = driver['last_name'],
        number = driver['driver_number'],
        team_name = driver['team_name'],
        country = driver['country_code'],
        headshot = driver['headshot_url']
    )

"""

positions_to_points = {
    1: 25,
    2: 18,
    3: 15,
    4: 12,
    5: 10,
    6: 8,
    7: 6,
    8: 4,
    9: 2,
    10: 1,
}

@login_required()
def logoutView(request):
    logout(request)
    return redirect('home')

def home(request):
    #se pueden hacer las request ya con una caracteristica   ?driver_number=1

    context = {}
    return render(request, 'base_templates/home.html', context)


def standings(request):
    drivers = Driver.objects.all()

    context = {'drivers': drivers}
    return render(request, 'base_templates/standings.html', context)

def predict(request):
    drivers = Driver.objects.all()

    context = {'drivers': drivers}
    return render(request, 'base_templates/predicts.html', context)

def last_race(): #tener ultima carrera
    return None
