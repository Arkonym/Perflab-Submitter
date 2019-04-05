from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
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
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

from perfapp.forms import *
from perfapp.tasks import *
from perfapp.models import *




def get_client_ip(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[-1].strip()
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip

def handle_upload(f, name, uid):
    path = "/code/uploads/"+str(uid)+"/"+name
    dest = open(path, 'w+')
    if f.multiple_chunks:
        for c in f.chunks():
            dest.write(c)
    else:
        dest.write(f.read())
    dest.close()

# Create your views here.

def home(request):
    users = User.objects.all()
    score_list = []
    for u in users:
        try:
            score_list+={"id":u.id, "score": u.profile.max_score}
        except Profile.DoesNotExist:
            score_list+={"id": u.id}
    context={
    "page_name": "Perflab Project",
    "u_list": users,
    "score_list": score_list
    }
    return render(request, "base.html", context=context)

@login_required(redirect_field_name='/', login_url="/login/")
def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    try:
        history = models.Attempts.objects.get(pk=user)
    except:
        history = []
    try:
        open_jobs = models.Jobs.objects.get(pk=user)
    except:
        open_jobs = []
    context={
        "title": "Profile",
        "user":user,
        "history": history,
        "open_jobs":open_jobs
    }
    return render(request, "profile.html", context=context)


@login_required(redirect_field_name='/', login_url="/login/")
def update_profile(request, user_id):
    user = User.objects.get(pk=user_id)

def logout_view(request):
    logout(request)
    return redirect("/home/")

def register(request):
    if request.method == "POST":
        form_instance = Registration(request.POST)
        if form_instance.is_valid():
            if form_instance.email_validate():
                form_instance.save()
                return redirect("/login/")
            # print("Hi")
    else:
        form_instance = Registration()
    context = {
        "form":form_instance,
    }
    return render(request, "registration/register.html", context=context)

@login_required(redirect_field_name='/', login_url='/login/')
def submitted(request):
    pass

@login_required(redirect_field_name='/', login_url='/login/')
def submit(request, user_id):
        print (get_client_ip(request))
        form = perfsubmission()
        servers = ""
        if request.method == 'POST':
            #print red.get('servers')
            form = perfsubmission(request)
            csrf = str(request.COOKIES['csrftoken'])
            try:
                os.chdir('/code/uploads/')
                a="mkdir ./"+str(user_id)
                b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
                b.wait()
                c = b.stdout.read()
                print (c)
                path = "/code/uploads/"+str(user_id)+"/config.txt"
                config = open(path, 'w+')
                if request.FILES['FilterMain']:
                    handle_uploaded_file(request.FILES['FilterMain'],"FilterMain.cpp",user_id)
                try:
                    if request.FILES['Makefile']:
                        handle_uploaded_file(request.FILES['Makefile'],"Makefile",user_id)
                        config.write("Makefile Y\n")
                except:
                    config.write("Makefile N\n")
                try:
                    if request.FILES['Filter_c']:
                        handle_uploaded_file(request.FILES['Filter_c'],"Filter.cpp",user_id)
                        config.write("Filter.cpp Y\n")
                except:
                    config.write("Filter.cpp N\n")
                try:
                    if request.FILES['Filter_h']:
                        handle_uploaded_file(request.FILES['Filter_h'],"Filter.h",user_id)
                        config.write("Filter.h Y\n")
                except:
                    config.write("Filter.h N\n")
                try:
                    if request.FILES['cs1300_c']:
                        handle_uploaded_file(request.FILES['cs1300_c'],"cs1300bmp.cc",user_id)
                        config.write("cs1300bmp.cc Y\n")
                except:
                    config.write("cs1300bmp.cc N\n")
                try:
                    if request.FILES['cs1300_h']:
                        handle_uploaded_file(request.FILES['cs1300_h'],"cs1300bmp.h",user_id)
                        config.write("cs1300bmp.h Y\n")
                except:
                    config.write("cs1300bmp.h N\n")
                config.close()
                return submitted(request)
            except:
                print ("except home")

        context={
            "title": "Submission Form",
            "form": form,
            "servers":servers
        }
        return render(request, "perf.html",context=context)


def score_update(request):
    return JsonResponse
