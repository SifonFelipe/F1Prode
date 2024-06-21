from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
import requests
from .models import Driver, Group, Prediction
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse


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

    
#se pueden hacer las request ya con una caracteristica   ?driver_number=1

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
    groups = Group.objects.all()

    context = {'groups': groups}
    return render(request, 'base_templates/home.html', context)


def standings(request):
    drivers = Driver.objects.all()

    context = {'drivers': drivers}
    return render(request, 'base_templates/standings.html', context)

def predict(request):
    drivers = Driver.objects.all()
    predictions_dict = {i: None for i in range(1, 20)}

    if request.method == "POST":
        for driver in drivers:
            prediction_input = request.POST.get(driver.first_name)
            predictions_dict[prediction_input] = driver.number

        prediction_instance = Prediction(user=request.user)
        prediction_instance.save_prediction(predictions_dict)

    context = {'drivers': drivers}
    return render(request, 'base_templates/predicts.html', context)

def view_prediction(request):
    prediction = Prediction.objects.get(user=request.user)
    print(prediction)

    prediction_dict = prediction.get_prediction()
    print(prediction_dict)

    context = {'predictions': prediction_dict}
    return render(request, 'base_templates/view_prediction.html', context)

@login_required()
def creategroup(request):
    if request.method == "POST":
        try:
            existing_name = Group.objects.get(name=request.POST.get('name'))
            return HttpResponse('Already exists a group with that name')

        except ObjectDoesNotExist or ValueError:
            None

        group_name = request.POST.get('name')
        group_description = request.POST.get('description')
        host = request.user

        Group.objects.create(
            name=group_name,
            description=group_description,
            host=host
        )

        group = Group.objects.get(name=group_name)
        group.participants.add(host)

        return redirect('home')


    context = {}
    return render(request, 'base_templates/create_group.html', context)

def viewgroup(request, groupname):
    group = Group.objects.get(name=groupname)
    context = {'group': group}
    return render(request, 'base_templates/view_group.html', context)