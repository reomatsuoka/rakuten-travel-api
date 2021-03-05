from django.db import models
from django.conf import settings

class Hotel(models.Model):
    number = models.IntegerField()

    def __str__(self):
        return str(self.number)

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hotelno = models.ManyToManyField(Hotel, blank=True)

    def __str__(self):
        return str(self.user)