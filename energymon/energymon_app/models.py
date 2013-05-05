from django.db import models

class Usage(models.Model):
    time_of_reading = models.DateTimeField()
    watts = models.IntegerField()

    def __unicode__(self):
        return '{}: {}'.format(self.time_of_reading, self.watts)


