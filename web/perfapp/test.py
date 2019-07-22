from __future__ import absolute_import
import sys, os, subprocess, django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "perfproject.settings")
django.setup()

from perfapp.models import Job, Attempt
from django.contrib.auth.models import User
print(User.objects.all())
