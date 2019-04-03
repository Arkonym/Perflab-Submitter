from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Server)
admin.site.register(models.Job)
admin.site.register(models.Attempt)
#admin.site.regist(User)
