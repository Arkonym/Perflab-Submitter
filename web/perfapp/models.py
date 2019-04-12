from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

import os
# Create your models here.

class Server(models.Model):
    ip = models.CharField(max_length=100)
    hostname = models.CharField(max_length=100, default="")
    uID = models.SmallIntegerField(blank=True, default=-1)
    inUse = models.BooleanField(default=False)


    def __str__(self):
        return self.hostname + " " + self.ip + " " + str(self.inUse)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    max_score = models.DecimalField(blank=True, null=True, max_digits=4, decimal_places=2)
    max_score_date = models.DateTimeField(null=True, blank=True)
    #django provides an automatic id field
    def __str__(self):
        return self.user.username

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

class Attempt(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now = True)
    score = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return self.time_stamp.strftime("%Y-%m-%d %H:%M:%S") + " (" + str(score)+ ")"

# def get_upload_path(instance, jid, filename):
#     return return '/code/uploads/{0}/{1}/{2}'

class Job(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    task_id= models.SmallIntegerField(blank=True, default=-1)
    time_stamp = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, default="New")
    percent_complete = models.SmallIntegerField(blank=True, default=0)
    config = models.FileField(blank=True, null=True)
    FilterMain = models.FileField(blank=True, null=True)
    Filter_c = models.FileField(blank=True, null=True)
    Filter_h = models.FileField(blank=True, null=True)
    Makefile = models.FileField(blank=True, null=True)
    cs1300_c = models.FileField(blank=True, null=True)
    cs1300_h = models.FileField(blank=True, null=True)

    def __str__(self):
        return self.owner +  self.time_stamp.strftime("%Y-%m-%d %H:%M:%S")
