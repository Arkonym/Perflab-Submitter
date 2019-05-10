from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db.models import F, Q
from django.core.files import File
from django.db import transaction

from django.template import Context
from django.template.loader import get_template, render_to_string
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.html import escape

from django.views.decorators.csrf import csrf_exempt

import sys,os,subprocess
from subprocess import Popen,PIPE
from redis import Redis
red = Redis(host='redis', port=6379)

from celery.task.control import revoke

#from perfapp.dhcp import *
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import datetime

from perfapp.forms import *
from perfapp.tasks import *
from perfapp.models import *
from perfapp.tables import ScoreTable




def get_client_ip(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[-1].strip()
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip

def handle_upload(job, f, f_name, j_path):
    path = j_path +"/"+f_name
    if f.multiple_chunks:
        with open(path, 'wb+') as dest:
            for c in f.chunks():
                dest.write(c)
    else:
        with open(path, 'w+') as dest:
            dest.write(f.read())
    dest.close()



# Create your views here.

def home(request):
    users = ScoreTable(User.objects.all(), '-profile.max_score')
    try:
        jobs = Job.objects.filter(Q(status='RUNNING')|Q(status='SCORING'))
    except:
        jobs=None
    context={
    "page_name": "Perflab Project",
    "u_list": users,
    "job_list": jobs
    }
    return render(request, "home.html", context=context)

@login_required(redirect_field_name='/', login_url="/login/")
def profile(request):
    user = request.user
    try:
        history = Attempt.objects.filter(owner=user).order_by('-score')[:8]
    except:
        history = None
    user.profile.max_score = history[0].score
    user.save()
    try:
        open_jobs = Job.objects.filter(owner=user)
    except:
        open_jobs = None
    try:
        logged_errors = Error.objects.filter(owner=user)
    except:
        logged_errors = None
    context={
        "title": "Profile",
        "user":user,
        "max_score": user.profile.max_score,
        "history": history,
        "open_jobs":open_jobs,
        "errors": logged_errors
    }
    return render(request, "profile.html", context=context)


@login_required(redirect_field_name='/', login_url="/login/")
def update_profile(request):
    user = request.user

def logout_view(request):
    logout(request)
    return redirect("/home/")

def register(request):
    if request.method == "POST":
        form_instance = Registration(request.POST)
        if form_instance.is_valid():
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
def submitted(request, j_id):
    # task = placeholder.delay()
    # job = Job.objects.filter(owner=request.user, jid = j_id)
    # job.task_id = task.task_id
    # print(task_id)
    context={
    "title":"Success",
    "job_id":j_id
    }
    return render(request, "success.html", context=context)

@login_required(redirect_field_name='/', login_url='/login/')
def submit(request):
        print (get_client_ip(request))
        servers = ""
        if request.method == 'POST':
            form = perfsubmission(request.POST, request.FILES)
            #print red.get('servers')
            if form.is_valid():
                try:
                    os.chdir('/perfserv/uploads/')
                    print(os.getcwd())
                except:
                    print("failed directory change")
                try:
                    a="mkdir ./"+ str(request.user.id)
                    b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
                    b.wait()
                except:
                    print("failed mkdir")
                try:
                    j_id = Job.objects.filter(owner=request.user).last().jid +1
                except:
                    #no jobs in table
                    j_id=1
                try:
                    print(j_id)
                    newJob = Job(jid=j_id,owner=request.user, note_field=form.cleaned_data["Note"])
                    newJob.save()
                except:
                     print('failed creating job')
                try:
                    path = "./"+str(request.user.id)+"/"+str(j_id)
                    print(path)
                    a = "mkdir "+ path
                    b = Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
                    b.wait()
                    con_path = path +"/config.txt"
                    config = open(con_path, 'w+')
                    print(con_path)
                except: print("failed writing config")
                try:
                    if request.FILES['FilterMain']:
                        handle_upload(newJob, request.FILES['FilterMain'],"FilterMain.cpp",path)
                    try:
                        if request.FILES['Makefile']:
                            handle_upload(newJob, request.FILES['Makefile'],"Makefile", path)
                            config.write("Makefile Y\n")
                    except:
                        config.write("Makefile N\n")
                    try:
                        if request.FILES['Filter_c']:
                            handle_upload(newJob, request.FILES['Filter_c'],"Filter.cpp", path)
                            config.write("Filter.cpp Y\n")
                    except:
                        config.write("Filter.cpp N\n")
                    try:
                        if request.FILES['Filter_h']:
                            handle_upload(newJob, request.FILES['Filter_h'],"Filter.h", path)
                            config.write("Filter.h Y\n")
                    except:
                        config.write("Filter.h N\n")
                    try:
                        if request.FILES['cs1300_c']:
                            handle_upload(newJob, request.FILES['cs1300_c'],"cs1300bmp.cc", path)
                            config.write("cs1300bmp.cc Y\n")
                    except:
                        config.write("cs1300bmp.cc N\n")
                    try:
                        if request.FILES['cs1300_h']:
                            handle_upload(newJob, request.FILES['cs1300_h'],"cs1300bmp.h", path)
                            config.write("cs1300bmp.h Y\n")
                    except:
                        config.write("cs1300bmp.h N\n")
                    config.close()

                    config = open(con_path, 'r')
                    # for line in config:
                    #     print(line)
                    newJob.config = File(config)
                    newJob.cur_action = "Waiting"
                    newJob.save()
                    return submitted(request, j_id)
                except:
                    newJob.delete()
                    print("except home")

            else:print("invalid form")
        else:
            form = perfsubmission()
        context={
            "title": "Submission Form",
            "form": form,
            "servers":servers
        }
        return render(request, "perf.html",context=context)

def progress(request, t_id):
    try:
        job = Job.objects.get(owner=request.user, id=t_id)
    except Job.DoesNotExist:
        job=None
    try:
        job_id = str(job.jid)
    except:
        job_id=""
    context={
        "title": "Open Job #"+job_id,
        "job" : job
    }
    return render(request, "progress.html", context=context)

def stop_job(request, j_id):
    job = Job.objects.get(owner=request.user, jid=j_id)
    job.status='STOPPED'
    job.cur_action='STOPPED'
    job.deletable=True
    revoke(job.task_id, terminate=True, signal='SIGUSR1')
    job.save()
    return HttpResponseRedirect(reverse('perfapp:Profile'))

def cancel_job(request, j_id):
    job = Job.objects.get(owner=request.user, jid=j_id)
    job.status='CANCELED'
    job.cur_action='CANCELED'
    job.save()
    job.delete()
    return HttpResponseRedirect(reverse('perfapp:Profile'))

def task_status_poll(request, id):
    try:
        status = Job.objects.get(owner=request.user, jid=id).status
    except: return HttpResponse('NOT_FOUND')
    return HttpResponse(status)

def task_action_poll(request, id):
    try:
        job = Job.objects.get(owner=request.user, jid=id)
        if(job.status=='COMPLETE' or job.status=='STOPPED'):
            raise()
    except: return HttpResponse('NOT_FOUND')
    cur_action = job.cur_action
    return HttpResponse(cur_action)

def clear_user_queue(request):
    user_jobs = Job.objects.filter(owner=request.user)
    for j in user_jobs:
        j.delete()
    user_jobs.delete()
    return HttpResponseRedirect(reverse('perfapp:Profile'))

def clear_error(request, e_id):
    error = Error.objects.get(owner=request.user, id=e_id)
    error.delete()
    return HttpResponseRedirect(reverse('perfapp:Profile'))
