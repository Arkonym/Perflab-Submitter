from django.db import models

# Create your models here.

class User(models.Model):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    #django provides an automatic id field

class Task(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10)
        class Meta:
            ordering= ["owner","time_stamp"]

    
