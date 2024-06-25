from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('predictions/', views.predict, name='predictions-page'),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', views.logoutView, name='logout-page'),
    path('creategroup/', views.creategroup, name='creategroup-page'),
    path('groups/<str:groupname>/', views.viewgroup, name='viewgroup-page'),
    path('predictions/self/', views.view_prediction_result, name='view-prediction-page'),
    path('updatedatabase/race/', views.update_database_race, name='update-database-race'),
    path('getresults/', views.get_results, name='getresults')
]