from django.db import models
from django.contrib.auth.models import User

class TimeStamp(models.Model):
    created_at=models.DateTimeField(auto_now_add=True, editable=False)
    updated_at=models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True

class Group(TimeStamp):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=64)

class Photo(TimeStamp):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    image = models.ImageField()