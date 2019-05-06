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
    online = models.BooleanField(default=True)


    def __str__(self):
        return self.hostname + " : " + self.ip + " : In Use(" + str(self.inUse) + ")"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    max_score = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)
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
    rel_id = models.PositiveSmallIntegerField(blank=True, null=True, default=0)
    time_stamp = models.DateTimeField(blank=True, null=True, default=None)
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, default=0)
    note_field = models.CharField(max_length=400, blank=True, null=True, default="")


    def __str__(self):
        if self.time_stamp!=None:
            return str(self.owner.id) + " : " +str(self.rel_id) + " : "+self.time_stamp.strftime("%Y-%m-%d %H:%M:%S") + " (" + str(self.score)+ ")"
        else: return str(self.owner.id) + " : " +str(self.rel_id) + " (" + str(self.score)+ ")"

    def save(self, *args, **kwargs):
        user_attempts = Attempt.objects.filter(owner=self.owner)
        if self.owner.profile.max_score ==None or self.owner.profile.max_score <= self.score:
            self.owner.profile.max_score = self.score
            self.owner.save()
        if len(user_attempts) >0:
            last_id = user_attempts.reverse()[0].rel_id
            self.rel_id = last_id+1
        else: self.rel_id=1
        super(Attempt, self).save(*args, **kwargs)
        if Attempt.objects.filter(owner=self.owner).count() > 15:
            top = Attempt.objects.filter(owner=self.owner).order_by('-score')[:8].values_list('id', flat=True)
            Attempt.objects.exclude(pk__in=list(top)).delete()



class Job(models.Model):
    jid = models.PositiveSmallIntegerField(blank=True, default=0) ##independent of primary key id
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    task_id= models.CharField(max_length=40, blank=True, null=True, default=None)
    hostname = models.CharField(max_length=100, default="")
    time_created = models.DateTimeField(auto_now_add=True)
    time_started = models.TimeField(blank=True, null=True, default=None)
    status = models.CharField(max_length=10, default="New")
    cur_action = models.CharField(max_length=50, default = None, blank=True, null=True)
    deletable = models.BooleanField(default=False)
    note_field = models.CharField(max_length=400, blank=True, null=True, default="")

    def __str__(self):
        return str(self.owner.id) + " : " + str(self.jid) + " : " + self.time_created.strftime("%Y-%m-%d %H:%M:%S")

    def delete(self, *args, **kwargs):
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
                #print(c)
        super(Job, self).delete(*args, **kwargs)


class Error(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    from_job_id = models.PositiveSmallIntegerField()
    time_stamp = models.DateTimeField(blank=True, null=True, default=None)
    errors = models.CharField(max_length= 500, blank=True, null=True, default=None)

    # def get_dir(instance):
    #     id = instance.owner.id
    #     if os.getcwd()!="/perfserv/uploads" or os.getcwd()!="/home/perfserv/uploads":
    #         try:
    #             os.chdir("/perfserv/uploads")
    #             if not os.path.isdir("./"+str(id)):
    #                 os.mkdir("./"+str(id)+"/errors")
    #             return "perfserv/uploads/"+ str(id) + "/errors"
    #         except:
    #             os.chdir("/home/perfserv/uploads")
    #             if not os.path.isdir("./"+str(id)):
    #                 os.mkdir("./"+str(id)+"/errors")
    #             return "/home/perfserv/uploads/"+ str(id) + "/errors"
    #     else: return "/errors"
