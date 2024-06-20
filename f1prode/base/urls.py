from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('standings/', views.standings, name='standings_page'),
    path('predictions/', views.predict, name='predictions_page'),
]