from django.db import models
from django.contrib.auth.models import User, Group
import json
from django.db.models.signals import post_save
from django.dispatch import receiver

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

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    predictions_json = models.TextField()
    race = models.TextField(max_length=70)
    year = models.IntegerField() 
    race_vinculated = models.ForeignKey('RaceInformation', on_delete=models.CASCADE)
    points_gained = models.IntegerField(default=0) #post-race
    succesfull = models.IntegerField(default=0) #post-race
    almost_succesfull = models.IntegerField(default=0) #post-race

    def save_prediction(self, predictions_dict):
        self.predictions_json = json.dumps(predictions_dict)
        self.save()

    def get_prediction(self):
        return json.loads(self.predictions_json) if self.predictions_json else {}

class RaceInformation(models.Model):
    race_name = models.TextField(max_length=70)
    year = models.IntegerField()
    race_start = models.DateTimeField()
    session_key = models.IntegerField()

    class Meta:
        ordering = ['-race_start']

class RaceResult(models.Model):
    results = models.TextField(max_length=1000)
    race_vinculated = models.OneToOneField(RaceInformation, on_delete=models.CASCADE)

    def save_result(self, race_results):
        self.results = json.dumps(race_results)
        self.save()

    def get_result(self):
        return json.loads(self.results) if self.results else {}

class GroupJoinRequests(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    state = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} a {self.group.name}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    successful_predicts = models.IntegerField(default=0)
    almost_predicts = models.IntegerField(default=0)

    class Meta:
        ordering = ['points']

    def __str__(self):
        return self.user.username

# Create profile when new user signs up
@receiver(post_save, sender=User)
def createProfile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()

class GroupDetails(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    description = models.TextField(max_length=1000)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    
    def __str__(self):
        return self.group.name