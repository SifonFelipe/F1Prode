from django.db import models
from django.contrib.auth.models import User
import json

class Driver(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    number = models.IntegerField()
    team_name = models.CharField(max_length=60)
    country = models.CharField(max_length=70)
    headshot = models.URLField(max_length=500)
    #points = models.IntegerField()

    def __str__(self):
        return self.last_name
    
class Group(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.name

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    predictions_json = models.TextField(max_length=1000)
    race = models.TextField(max_length=200)
    year = models.IntegerField() 
    race_vinculated = models.ForeignKey('RaceInformation', on_delete=models.CASCADE)

    def save_prediction(self, predictions_dict):
        self.predictions_json = json.dumps(predictions_dict)
        self.save()

    def get_prediction(self):
        return json.loads(self.predictions_json) if self.predictions_json else {}

class RaceInformation(models.Model):
    race_name = models.TextField(max_length=200)
    year = models.IntegerField()
    race_start = models.DateTimeField()

class RaceResult(models.Model):
    results = models.TextField(max_length=1000)
    race_vinculated = models.OneToOneField(RaceInformation, on_delete=models.CASCADE)

    def save_result(self, race_results):
        self.results = json.dumps(race_results)
        self.save()

    def get_result(self):
        return json.loads(self.results) if self.results else {}