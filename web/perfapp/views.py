from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.db.models import F
from django.db import transaction

from django.template import Context
from django.template.loader import get_template
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.html import escape

from django.views.decorators.csrf import csrf_exempt

import sys,os,subprocess
from subprocess import Popen,PIPE
from redis import Redis
red = Redis(host='redis', port=6379)

#from perfapp.dhcp import *

from datetime import datetime

from perfapp.forms import *
from perfapp.tasks import *
from perfapp.models import *


from datetime import datetime


def get_client_ip(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[-1].strip()
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip

def handle_upload(f, name, token):
    path = "/code/uploads/"+str(token).rstrip().lstrip()+"/"+name
    dest = open(path, 'w+')
    if f.multiple_chunks:
        for c in f.chunks():
            dest.write(c)
    else:
        dest.write(f.read())
    dest.close()

# Create your views here.

def home(request):
    context={
        "body": "This is the body",
        "page_title": "This is the page title"
    }
    return render(request, "base.html", context=context)

def profile(request):
    pass




def scoreboard(request):
    pass
