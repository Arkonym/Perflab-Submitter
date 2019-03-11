from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class Servers(models.Model):
    ip = models.CharField(max_length=100)
    hostname = models.CharField(max_length=100, default="")
    inUse = models.BooleanField(default=False)

    def __str__(self):
        return self.hostname + " " + self.ip + " " + str(self.inUse)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_login =models.DateTimeField()
    max_score = models.DoubleField()
    #django provides an automatic id field
    def __str__(self):
        return self.last_name

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

class Attempts(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now = True)
    score = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return self.time_stamp.strftime("%Y-%m-%d %H:%M:%S") + " (" + str(score)+ ")"


class Jobs(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10)

    def __str__(self):
        return self.owner +  self.time_stamp.strftime("%Y-%m-%d %H:%M:%S")
    # class Meta:
    #     ordering= ["owner","time_stamp"]
