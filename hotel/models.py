from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    number = models.CharField(max_length=10)
    floor = models.IntegerField()
    description = models.TextField()

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()

    # class Meta:
    #     unique_together = ('room', 'check_in')