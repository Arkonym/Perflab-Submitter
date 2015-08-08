from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.db.models import F

from django.template import Context
from django.template.loader import get_template
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.html import escape

from django.views.decorators.csrf import csrf_exempt

import sys,os,subprocess
from subprocess import Popen,PIPE
from redis import Redis
red = Redis(host='redis2', port=6379)
red.set('servers',2)


from datetime import datetime

from perfapp.forms import *
from perfapp.tasks import *

# Create your views here.

def get_client_ip(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[-1].strip()
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip

##Method to write save uploaded file to folder created from user's csrftoken
def handle_uploaded_file(f,name,token):
    path = "/code/uploads/"+str(token).rstrip().lstrip()+"/"+name
    dest = open(path, 'w+')
    if f.multiple_chunks:
        for c in f.chunks():
            dest.write(c)
    else:
        dest.write(f.read())
    dest.close() 
    

def home(request):
    print get_client_ip(request)
    form = perfsubmission()
    if request.method == 'POST':
        form = perfsubmission(request)
        csrf = str(request.COOKIES['csrftoken'])
        try:
            os.chdir('/home/website/uploads/')
            a="mkdir ./"+str(csrf).rstrip().lstrip()
            b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
            b.wait()
            c = b.stdout.read()
            print c
            path = "/home/website/uploads/"+str(csrf).rstrip().lstrip()+"/config.txt"
            config = open(path, 'w+')
            if request.FILES['FilterMain']:
                handle_uploaded_file(request.FILES['FilterMain'],"FilterMain.cpp",csrf)                
            try:
                if request.FILES['Makefile']:
                    handle_uploaded_file(request.FILES['Makefile'],"Makefile",csrf)
                    config.write("Makefile Y\n")
            except:
                config.write("Makefile N\n")
            try:
                if request.FILES['Filter_c']:
                    handle_uploaded_file(request.FILES['Filter_c'],"Filter.cpp",csrf)
                    config.write("Filter.cpp Y\n")
            except:
                config.write("Filter.cpp N\n")                
            try:
                if request.FILES['Filter_h']:
                    handle_uploaded_file(request.FILES['Filter_h'],"Filter.h",csrf)
                    config.write("Filter.h Y\n")
            except:
                config.write("Filter.h N\n")
            try:
                if request.FILES['cs1300_c']:
                    handle_uploaded_file(request.FILES['cs1300_c'],"cs1300bmp.cc",csrf)
                    config.write("cs1300bmp.cc Y\n")
            except:
                config.write("cs1300bmp.cc N\n")
            try:
                if request.FILES['cs1300_h']:
                    handle_uploaded_file(request.FILES['cs1300_h'],"cs1300bmp.h",csrf)
                    config.write("cs1300bmp.h Y\n")
            except:
                config.write("cs1300bmp.h N\n")
            config.close()
            return submit(request)
        except:
            print "except home",
    #print "what"        
    response = render(request, 'perf.html', {
        'page_name': 'Submission',
        'form': form
    })
	#return HttpResponse("Hello, world. You're at the poll index.")
	# Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, we default to zero and cast that.
    #pq = pqueue()
    #print pq.queue(request.COOKIES['csrftoken'])
    
    return response
    
def get_celery_worker_status():
    ERROR_KEY = "ERROR"
    try:
        from celery.task.control import inspect
        insp = inspect()
        d = insp.stats()
        if not d:
            d = { ERROR_KEY: 'No running Celery workers were found.' }
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the RabbitMQ server is running.'
        d = { ERROR_KEY: msg }
    except ImportError as e:
        d = { ERROR_KEY: str(e)}
    return d

def test(request):
    response = render(request, 'test2.html')
    return response
    #a="celery -A perfproject inspect stats"    
    #b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
    #b.wait()
    #c = b.stdout.read()
    #print c
    #print get_celery_worker_status()
    if int(red.get('servers'))>0:
        toReturn = "There are " + red.get('servers') + " servers"
        red.decr('servers')
        taskid = testing.delay(int(red.get('servers'))+1)
        taskid.wait()
        toReturn = taskid.get()
        #testing("test")
    else:
        toReturn = "No Servers"
    return HttpResponse(toReturn)

def test2(request):
    return HttpResponse("Hello World")

def test3(request):
    return HttpResponse("Hello World2")