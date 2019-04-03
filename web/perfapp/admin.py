from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Servers)
admin.site.register(models.Jobs)
admin.site.register(models.Attempts)
admin.site.register(models.Profile)
#admin.site.regist(User)
