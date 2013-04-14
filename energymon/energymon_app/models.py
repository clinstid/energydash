from django.db import models

# Create your models here.
class Usage(models.Model):
    time_of_reading = models.DateTimeField()
    watts = models.IntegerField()

