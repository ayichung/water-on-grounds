from django.db import models
from django.contrib.auth.models import User
# from django.conf import settings

def get_null_user():
    return User.objects.get_or_create(username="NULL_USER")[0]

# blank = False requires column as a field in a form (cannot submit without)
# null = False requires column to have a value (cannot be NULL)
class Building(models.Model):
    name = models.CharField(max_length=500)
    lat = models.FloatField()
    lng = models.FloatField()
    place_id = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class WaterStation(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET(get_null_user)) # user who submitted, if user is deleted set to NULL_USER (dummy user)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    floor = models.IntegerField(default=1, blank=False) # 0 is basement, 1 is first, etc., should limit in form
    CHOICES = (('c', 'Central area'), ('n', 'North side'), ('s', 'South side'), ('e', 'East side'), ('w', 'West side'))
    cardinal = models.CharField(max_length=1, blank=False, default=None, choices=CHOICES) # one of n, s, e, w, c (center of building)
    traditional = models.BooleanField() # true is bubbler / bottom part
    bottle = models.BooleanField() # true is vertical water bottle filler
    # image = models.ImageField(upload_to=MEDIA_ROOT, blank=True, null=True) # image of station, if NULL do not display
    approved = models.BooleanField() # true is approved and will show from map, false will show on admin approval page