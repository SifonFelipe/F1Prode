from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
import requests
from .models import Driver, Group, Prediction, RaceResult, RaceInformation, Profile, GroupJoinRequests, GroupDetails
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from datetime import datetime, timedelta, timezone
from django.contrib.auth.models import Group, User
from django.contrib import messages

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

def compare(results=dict(), predictions=dict()):
    acertados = 0
    casi_acertados = 0

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
    information = [posiciones_acertadas, posiciones_casi_acertadas, puntos]
    return information


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

            result = RaceResult.objects.create(race_vinculated=race_vinculated)
            result.save_result(dict_ordenado)

            results = result.get_result()

            race_predictions = Prediction.objects.filter(race_vinculated=race_vinculated)

            for race_prediction in race_predictions:
                user = race_prediction.user
                user_profile = Profile.objects.get(user=user)
    
                user_predictions_dict = race_prediction.get_prediction()
                prediction_results = compare(results, user_predictions_dict)
                race_prediction.points_gained = prediction_results[2]
                race_prediction.save()

                user_predictions = Prediction.objects.filter(user=user)
                points_to_set = 0

                for user_prediction in user_predictions:
                    points_to_set += user_prediction.points_gained

                user_profile.points = points_to_set
                user_profile.save()

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

def view_prediction_result(request):
    try:
        race_object = RaceInformation.objects.latest('-race_start')
        prediction_object = Prediction.objects.get(user=request.user, race_vinculated=race_object)
        results_object = RaceResult.objects.get(race_vinculated=race_object)
    except:
        return HttpResponse('you didnt predict yet or the race didnt end')

    driver_ordenados = []
    predicts_ordenadas = []
    results = results_object.get_result()
    predictions = prediction_object.get_prediction()

    for result in results:
        driver = Driver.objects.get(number=results[result])
        driver_ordenados.append(driver)

    for predict in predictions:
        driver_predict = Driver.objects.get(number=predictions[predict])
        predicts_ordenadas.append(driver_predict)

    context = {'drivers_ordenados': driver_ordenados, 'predicts_ordenadas': predicts_ordenadas, 'puntos': prediction_object.points_gained}
    return render(request, 'base_templates/view_prediction_results.html', context)

@login_required()
def logoutView(request):
    logout(request)
    return redirect('home')

def home(request):
    return render(request, 'base_templates/home.html')

def create_groups(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        host = request.user
        
        group = Group.objects.create(name=name)

        group_details = GroupDetails.objects.create(
            group=group,
            host=host,
            description=description,
        )

        group_details.participants.clear()
        group_details.participants.add(host)

    return render(request, 'base_templates/create_group.html')

def see_groups(request):
    groups = Group.objects.all()
    context = {'groups': groups}
    return render(request, 'base_templates/groups.html', context)

def view_group(request, group_id):
    group = Group.objects.get(id=group_id)
    group_details = GroupDetails.objects.get(group=group)
    users = [x for x in group_details.participants.all()]

    points_list = []
    users_list = []
    for user in users:
        instance_profile = Profile.objects.get(user=user)
        points_user = instance_profile.points
        points_list.append(points_user)
        points_list.sort()
        users_list.insert(points_list.index(points_user), instance_profile)

    users_list.reverse()

    context = {'group': group_details, 'participants': users_list, 'group_object': group}
    return render(request, 'base_templates/view_group.html', context)

@login_required
def request_group_join(request, group_id):
    group = Group.objects.get(id=group_id)
    existing_request = GroupJoinRequests.objects.filter(user=request.user, group=group)
    
    if not existing_request:
        GroupJoinRequests.objects.create(user=request.user, group=group)

    return redirect('home')

def manage_group_requests(request):
    if request.method == "POST":
        
        for key in request.POST.keys():
            if request.POST[key] in ['Accept', 'Reject']:
                request_touched = GroupJoinRequests.objects.get(id=key)

                if request.POST[key] == 'Accept':
                    user = request_touched.user
                    group_to_add = GroupDetails.objects.get(group=request_touched.group)
                    group_to_add.participants.add(user)
    
                request_touched.delete()
                break

    try:
        get_groups = GroupDetails.objects.filter(host=request.user)
        has_groups = True
    except:
        has_groups = False

    if has_groups == True:
        group_requests_dict = {i.group: [] for i in get_groups}

        for group in get_groups:
            group_requests = GroupJoinRequests.objects.filter(group=group.group)
            for join_request in group_requests:
                group_requests_dict[group.group].append(join_request)

    context = {'has_groups': has_groups, 'requests': group_requests_dict}
    return render(request, 'base_templates/manage_requests.html', context)