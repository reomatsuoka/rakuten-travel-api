from django.db import models
from django.conf import settings
from django.utils import timezone


class Area(models.Model):
    middle_class_name = models.CharField("都道府県名", max_length=20, blank=False)
    small_class_name = models.CharField("市名", max_length=20, blank=False)
    detail_class_name = models.CharField("詳細地名", max_length=20, blank=True)
    checkin_date = models.DateField(blank=False, null=False)
    checkout_date = models.DateField(blank=False, null=False)
    default_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.middle_class_name)


class Hotel(models.Model):
    number = models.IntegerField()

    def __str__(self):
        return str(self.number)

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hotelno = models.ManyToManyField(Hotel, blank=True)

    def __str__(self):
        return str(self.user)