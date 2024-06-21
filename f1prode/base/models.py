from django.db import models

class Driver(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    number = models.IntegerField()
    team_name = models.CharField(max_length=60)
    country = models.CharField(max_length=70)
    headshot = models.URLField(max_length=500)
    numero_string = str(number)
    div_number = "div" + numero_string
    #points = models.IntegerField()

    def __str__(self):
        return self.last_name