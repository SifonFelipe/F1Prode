from django.shortcuts import render
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

def home(request):
    f1_data = requests.get('https://api.openf1.org/v1/drivers').json()
    #se pueden hacer las request ya con una caracteristica   ?driver_number=1
    #['session_key'] es el valor de cada sesion y es igual por cada participante de la sesion
    f1_data_drivers = f1_data[-20:]

    context = {'data': f1_data_drivers}
    return render(request, 'base/home.html', context)


def standings(request):
    drivers = Driver.objects.all()

    context = {'drivers': drivers}
    return render(request, 'base/standings.html', context)