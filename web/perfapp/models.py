from django.db import models
from datetime import datetime

# Create your models here.

class Servers(models.Model):
    ip = models.CharField(max_length=100)
    hostname = models.CharField(max_length=100, default="")
    inUse = models.BooleanField(default=False)

    def __str__(self):
        return self.hostname + " " + self.ip + " " + str(self.inUse)

class User(models.Model):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    email = models.EmailField
    max_score = models.IntegerField()
    #django provides an automatic id field
    def __str__(self):
        return self.last_name

class Attempt(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now = True)
    score = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return self.time_stamp.strftime("%Y-%m-%d %H:%M:%S") + " (" + str(score)+ ")"


class Job(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10)

    def __str__(self):
        return self.owner +  self.time_stamp.strftime("%Y-%m-%d %H:%M:%S")
    # class Meta:
    #     ordering= ["owner","time_stamp"]
