from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
import requests
from .models import Driver, Group, Prediction, RaceResult, RaceInformation, Profile
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from datetime import datetime, timedelta, timezone


"""
API documentation
https://openf1.org/
https://github.com/br-g/openf1

    f1_data = requests.get('https://api.openf1.org/v1/drivers').json()
    f1_data_drivers = f1_data[-20:]
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

def makedict(prediction=list(), drivers=list()):
    new_dict = {i: None for i in range(1, 21)}
    for predict, driver in zip(prediction, drivers):
        predict_number = int(predict)
        new_dict[predict_number] = driver

    return new_dict

def transformint(dictionary=dict()):
    new_dict = {i: None for i in range(1, 21)}
    for dict_key in dictionary:
        new_dict[int(dict_key)] = dictionary[dict_key]

    return new_dict

def order_dict(dictionary=dict()):
    new_dict = {i: None for i in range(1, 21)}
    for dict_key in dictionary:
        new_dict[dict_key] = dictionary[dict_key]

    return new_dict

def get_results(request):
    if request.method == "POST":
        if request.user.username == 'sifon':
            race_vinculated = RaceInformation.objects.latest('-race_start')
            race_vinculated_session_key = race_vinculated.session_key
            results = requests.get(f'https://api.openf1.org/v1/position?session_key={race_vinculated_session_key}').json()

            dict_positions = {i: None for i in range(1, 21)}
            for driver in reversed(results):
                if dict_positions[driver['position']] == None:
                    dict_positions[driver['position']] = driver['driver_number']

            dict_ordenado = order_dict(dict_positions)

            instance = RaceResult.objects.create(race_vinculated=race_vinculated)
            instance.save_result(dict_ordenado)

    return render(request, 'base_templates/get_results.html')

def update_database_race(request):
    if request.method == "POST":
        if request.user.username == 'sifon':
            race_name = request.POST.get('race-name') #circuit short name
            year = datetime.now().year
            
            race = requests.get(f"https://api.openf1.org/v1/sessions?year={year}&session_name=Practice 1&circuit_short_name={race_name}").json()
        
            if race != []:
                check_time = race[0]['date_start']
                start_time = datetime.fromisoformat(check_time) + timedelta(hours=47)

                session_key = race[0]['session_key'] + 7

                RaceInformation.objects.create(
                    race_name = race_name,
                    year = year,
                    race_start = start_time,
                    session_key = session_key,
                )

    context = {}
    return render(request, 'base_templates/update_database.html', context)

def predict(request):
    drivers = Driver.objects.all()
    predictions_dict = {}

    if request.method == "POST":
        race_selected = RaceInformation.objects.latest('-race_start')

        race_start = race_selected.race_start
        hoy = datetime.now(timezone.utc)
        hoy_format = hoy.replace(tzinfo=timezone.utc).astimezone(tz=timezone(timedelta(hours=0)))
        #if hoy_format > race_start:
            #return HttpResponse('The race has already started')

        predictions_inputs = []
        drivers_numbers = []

        for driver in drivers:
            prediction_input = request.POST.get(driver.first_name)
            driver_number = driver.number
            
            predictions_inputs.append(prediction_input)
            drivers_numbers.append(driver_number)

            if prediction_input == '':
                return HttpResponse('No pusiste todos los resultados!!!')
            
        try:
            existing_prediction = Prediction.objects.get(race_vinculated=race_selected, user=request.user)
            existing_prediction.delete()
        except:
            None    

        predictions_dict = makedict(predictions_inputs, drivers_numbers)

        prediction_instance = Prediction.objects.create(
            user=request.user,
            race=race_selected.race_name,
            year=race_selected.year,
            race_vinculated=race_selected,
        )

        prediction_instance.save_prediction(predictions_dict)
        return redirect('home')

    context = {'drivers': drivers}
    return render(request, 'base_templates/predicts.html', context)

def compare(results=dict(), predictions=dict()):
    acertados = 0
    casi_acertados = 0

    information = []
    posiciones_acertadas = []
    posiciones_casi_acertadas = []
    results = transformint(results)
    predictions = transformint(predictions)

    for result_key, predict_key in zip(results, predictions):
        result = results[result_key]
        predict = predictions[predict_key]

        if result == predict:
            acertados += 1
            posiciones_acertadas.append(predict_key)
        elif result_key != 1 and result_key != 20:
            if predict == results[result_key + 1] or predict == results[result_key - 1]:
                casi_acertados += 1
                posiciones_casi_acertadas.append(predict_key)
        elif result_key == 1:
            if predict == results[result_key + 1]:
                casi_acertados += 1
                posiciones_casi_acertadas.append(predict_key)
        elif result_key == 20:
            if predict == results[result_key - 1]:
                casi_acertados += 1
                posiciones_casi_acertadas.append(predict_key)

    puntos = acertados * 3 + casi_acertados

    information.append(posiciones_acertadas)
    information.append(posiciones_casi_acertadas)
    information.append(puntos)
    return information

def view_prediction_result(request):
    try:
        race_object = RaceInformation.objects.latest('-race_start')
        prediction_object = Prediction.objects.get(user=request.user, race_vinculated=race_object)
        results_object = RaceResult.objects.get(race_vinculated=race_object)
    except:
        return HttpResponse('you didnt predict yet or the race didnt end')

    predictions = prediction_object.get_prediction()
    results = results_object.get_result()
    information = compare(results, predictions)

    posiciones_acertadas = information[0]
    posiciones_casi_acertadas = information[1]
    puntos = information[2]

    if prediction_object.points_gained == 0:
        prediction_object.points_gained = puntos
        prediction_object.save()

    driver_objects_ordenados = []
    predicts_ordenadas = []

    for result in results:
        driver = Driver.objects.get(number=results[result])
        driver_objects_ordenados.append(driver)

    for predict in predictions:
        driver_predict = Driver.objects.get(number=predictions[predict])
        predicts_ordenadas.append(driver_predict)

    context = {'predicts_ordenadas': predicts_ordenadas, 'drivers_ordenados': driver_objects_ordenados,'posiciones_acertadas': posiciones_acertadas, 'posiciones_casi_acertadas': posiciones_casi_acertadas, 'puntos': puntos}
    return render(request, 'base_templates/view_prediction_results.html', context)


@login_required
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

@login_required
def viewgroup(request, groupname):
    group = Group.objects.get(name=groupname)
    context = {'group': group}
    return render(request, 'base_templates/view_group.html', context)

@login_required()
def logoutView(request):
    logout(request)
    return redirect('home')

def home(request):
    groups = Group.objects.all()

    context = {'groups': groups}
    return render(request, 'base_templates/home.html', context)
