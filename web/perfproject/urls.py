"""perfproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

import os.path
site_media = os.path.join(os.path.dirname(__file__), 'site_media')
#shibsso = os.path.join(os.path.dirname(__file__), 'django-shibsso/shibsso')

from perfapp import views as perfapp

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('perfapp.urls')),
    path('/celery_progress/', include('celery_progress.urls')),

]

#no good way to do this, but it works
"""comment out before migrations"""
# from perfapp.models import Job
# jobs =Job.objects.all()
# for j in jobs:
#     j.delete()
# Job.objects.all().delete()
