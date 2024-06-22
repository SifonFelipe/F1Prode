from django.contrib import admin
from .models import Driver, Group, Prediction, RaceResult, RaceInformation

admin.site.register(Driver)
admin.site.register(Group)
admin.site.register(Prediction)
admin.site.register(RaceResult)
admin.site.register(RaceInformation)