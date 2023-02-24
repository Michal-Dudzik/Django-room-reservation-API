from django.db import models
from django.contrib.auth.models import User, AbstractUser

class Room(models.Model):
    number = models.IntegerField()
    floor = models.IntegerField()
    description = models.CharField(max_length=500)

    def __str__(self):
        return str(self.number) + ' - ' + str(self.floor) + ' - ' + self.description
    
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return self.user + ' - ' + self.room + ' - ' + self.date
    
class User(AbstractUser):
    pass