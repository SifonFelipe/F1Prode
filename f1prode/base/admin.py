from django.contrib import admin
from .models import Driver, Prediction, RaceResult, RaceInformation, Profile, GroupJoinRequests, GroupDetails

admin.site.register(Driver)
admin.site.register(Prediction)
admin.site.register(RaceResult)
admin.site.register(RaceInformation)
admin.site.register(Profile)
admin.site.register(GroupJoinRequests)
admin.site.register(GroupDetails)