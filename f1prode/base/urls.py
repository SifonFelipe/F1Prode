from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('predictions/', views.predict, name='predictions-page'),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', views.logoutView, name='logout-page'),
    path('predictions/self/', views.view_prediction_result, name='view-prediction-page'),
    path('updatedatabase/race/', views.update_database_race, name='update-database-race'),
    path('getresults/', views.get_results, name='getresults'),
    path('groups/', views.see_groups, name='groups-page'),
    path('groups/<str:group_id>', views.view_group, name='view-group-page'),
    path('groups/create/', views.create_groups, name='create-group-page'),
    path('groups/<str:group_id>/join/', views.request_group_join, name='request-group-page'),
    path('groups/manage-requests/', views.manage_group_requests, name='manage-requests-page'),
]