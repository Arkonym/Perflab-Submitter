from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

import os
from subprocess import Popen, PIPE
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
    time_stamp = models.DateTimeField()
    score = models.DecimalField(max_digits=4, decimal_places=2, blank=True, default=0)
    note_field = models.CharField(max_length=400, blank=True, null=True, default="")

    def __str__(self):
        return str(self.owner.id) + " : " +self.time_stamp.strftime("%Y-%m-%d %H:%M:%S") + " (" + str(self.score)+ ")"

# @receiver(post_save, sender=Attempt)
# def update_job_id(sender, instance, created, *args, **kwargs):
#     if created:
#         related_jobs = Job.objects.filter(owner=instance.owner)
#         jid=1
#         for j in related_jobs:
#             j.id=jid
#             j.save()
#             jid+=1


class Job(models.Model):
    jid = models.PositiveSmallIntegerField(blank=True, default=0) ##independent of primary key id
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    task_id= models.CharField(max_length=40, blank=True, null=True, default="")
    time_created = models.DateTimeField(auto_now_add=True)
    time_started = models.TimeField(blank=True, null=True, default=None)
    status = models.CharField(max_length=10, default="New")
    deletable = models.BooleanField(default=False)
    percent_complete = models.SmallIntegerField(blank=True, default=0)
    config = models.FileField(blank=True, null=True)
    FilterMain = models.FileField(blank=True, null=True)
    Filter_c = models.FileField(blank=True, null=True)
    Filter_h = models.FileField(blank=True, null=True)
    Makefile = models.FileField(blank=True, null=True)
    cs1300_c = models.FileField(blank=True, null=True)
    cs1300_h = models.FileField(blank=True, null=True)
    note_field = models.CharField(max_length=400, blank=True, null=True, default="")

    def __str__(self):
        return str(self.owner.id) + " : " + str(self.jid) + " : " + self.time_stamp.strftime("%Y-%m-%d %H:%M:%S")

    def delete(self, *args, **kwargs):
        if self.config:
            if os.getcwd()!="/perfserv/uploads" or os.getcwd()!="/home/perfserv/uploads":
                try:
                    os.chdir("/perfserv/uploads")
                except:
                    os.chdir("/home/perfserv/uploads")
                if os.path.exists("./"+str(self.owner.id)):
                    os.chdir("./"+str(self.owner.id))
                    a = "rm -r ./"+ str(self.jid)
                    b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
                    b.wait()
                    c= b.stdout.read()
                    print(c)
        super(Job, self).delete(*args, **kwargs)
