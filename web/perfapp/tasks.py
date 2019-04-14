from __future__ import absolute_import
from celery import shared_task, task
from celery.utils.log import get_task_logger
from celery_progress.backend import ProgressRecorder
from perfapp.models import Job, Attempt
from django.contrib.auth.models import User

from time import sleep
import sys, os, subprocess
from subprocess import Popen, PIPE

from redis import Redis
red = Redis(host='redis', port=6379)

logger=get_task_logger(__name__)

@shared_task
def cleanup():
    try:
        jobs = Job.objects.all()
        print(jobs)
    except Job.DoesNotExist:
        return "empty jobs"
    for j in jobs:
        if j.deletable==True:
            print(str(j.owner) + " : " +str(j))
            j.delete()
    return "cleanup complete"
@shared_task()
def dummyTask(j_id, uid):
    print(j_id)
    print(uid)
    user = User.objects.get(id=uid)
    job = Job.objects.get(owner=user, jid=j_id)
    job.status='RUNNING'
    job.save()
    progress_recorder = ProgressRecorder(self)
    for i in range(100):
        sleep(1)
        progress_recorder.set_progress(i+1, 100)
        job.percent_complete=i+1
        job.save()
    job.status='COMPLETE'
    newAttempt = Attempt(owner=user, note_field=job.note_field, score=79.99, time_stamp=job.time_stamp)
    job.deletable=True
    job.save()

@shared_task(bind=True)
def runLab(j_id,uid,server,hostname):
    owner = User.objects.get(id=uid)
    job = Job.objects.get(owner=user, jid=j_id)
    progress_recorder = ProgressRecorder(self)
    #current_task.update_state(state='PROGRESS', meta={'current': 0, 'total': 100})
    toReturn = ""
    try:
        path = "/perfserv/uploads/"+str(uid)+"/"+str(j_id)
        #print path
        config = open(path + "config.txt","r")
        progress_recorder.set_progress(1, 100)
        #current_task.update_state(state='PROGRESS', meta={'current': 1, 'total': 100})
        a="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"rm -rf perflab-setup\""
        b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
        b.wait()
        c = b.stdout.read()
        progress_recorder.set_progress(2, 100)
        #current_task.update_state(state='PROGRESS', meta={'current': 2, 'total': 100})
        a="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"cp -rf perflab-files perflab-setup\""
        b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
        b.wait()
        c = b.stdout.read()
        progress_recorder.set_progress(3, 100)
        #current_task.update_state(state='PROGRESS', meta={'current': 3, 'total': 100})
        f = open(path+"FilterMain.cpp","r")
        for line in f:
            if "unistd" in line:
                return "Illegal Library unistd"
        a="scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "+path+"FilterMain.cpp perfuser@"+server+":~/perflab-setup/"
        b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
        b.wait()
        c = b.stdout.read()
        progress_recorder.set_progress(4, 100)
        #current_task.update_state(state='PROGRESS', meta={'current': 4, 'total': 100})
        for line in config:
        	#print line
            line = line.split()
            if line[1]=="Y":
                f = open(path+line[0],"r")
                print (line[0])
                for line2 in f:
                    if "unistd" in line2:
                        return "Illegal Library unistd"
                a="scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "+path+str(line[0])+" perfuser@"+server+":~/perflab-setup/"
                print (a)
                b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
                b.wait()
                c = b.stdout.read()
        progress_recorder.set_progress(5, 100)
        #current_task.update_state(state='PROGRESS', meta={'current': 5, 'total': 100})
        a="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"cd perflab-setup/ ; make filter\""
        b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
        b.wait()
        c = b.stdout.read()
        e = b.stderr.read()
        if len(e)>0:
            if "Error" in e:
                return e
            #print e
            if not "ECDSA" in e:
                return e
        #print c
        progress_recorder.set_progress(10, 100)
        #current_task.update_state(state='PROGRESS', meta={'current': 10, 'total': 100})
        status = 10.0
        tests = 5
        increment = (100.0-status)/(4.0*float(tests))
        scores = []
        #GAUSS
        gauss = []
        count = 0
        while count < tests:
            a="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"cd perflab-setup/ ; ./gauss.sh\""
            print (a)
            b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
            b.wait()
            c = b.stdout.read()
            line = c.split()
            try:
                print (line)
                score = float(line[-1])
                print (score)
                if not score > 9000 and not score <=0: # Check for and ignore odd scores
                    scores = scores + [score]
                    gauss = gauss + [score]
                    status = status + increment
                    count = count + 1
                    progress_recorder.set_progress(status, 100)
                    #current_task.update_state(state='PROGRESS', meta={'current': status, 'total': 100})
            except:
                return "gauss " + str(sys.exc_info()) + " " + hostname + " " + str(c) + "\n"+ str(a) + "\n" + str(b.stderr.read())

        #AVG
        count = 0
        avg = []
        while count < tests:
            a="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"cd perflab-setup/ ; ./avg.sh\""
            b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
            b.wait()
            c = b.stdout.read()
            line = c.split()
            try:
                score = float(line[-1])
                if not score > 9000 and not score <=0: # Check for and ignore odd scores
                    scores = scores + [score]
                    avg = avg + [score]
                    status = status + increment
                    count = count + 1
                    #current_task.update_state(state='PROGRESS', meta={'current': status, 'total': 100})
            except:
                return "avg " + str(sys.exc_info())+ " " + hostname

        #HLINE
        count = 0
        hline = []
        while count < tests:
            a="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"cd perflab-setup/ ; ./hline.sh\""
            b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
            b.wait()
            c = b.stdout.read()
            line = c.split()
            try:
                score = float(line[-1])
                if not score > 9000 and not score <=0: # Check for and ignore odd scores
                    scores = scores + [score]
                    hline = hline + [score]
                    status = status + increment
                    count = count + 1
                    #current_task.update_state(state='PROGRESS', meta={'current': status, 'total': 100})
            except:
                return "hline " + str(sys.exc_info()) + " " + hostname

        #EMBOSS
        count = 0
        emboss = []
        while count < tests:
            a="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"cd perflab-setup/ ; ./emboss.sh\""
            b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
            b.wait()
            c = b.stdout.read()
            e = b.stderr.read()
            line = c.split()
            #print c
            try:
                score = float(line[-1])
                if not score > 9000 and not score <=0: # Check for and ignore odd scores
                    scores = scores + [score]
                    emboss = emboss + [score]
                    status = status + increment
                    count = count + 1
                    #current_task.update_state(state='PROGRESS', meta={'current': status, 'total': 100})
            except:
                #print e
                return  "emboss " + str(sys.exc_info()) + " " + hostname

        scores.sort()
        #print scores



        toReturn += "gauss: "
        for g in gauss:
            toReturn += str(g) + ".. "
        toReturn += "\navg: "
        for a in avg:
            toReturn += str(a) + ".. "
        toReturn += "\nhline: "
        for h in hline:
            toReturn += str(h) + ".. "
        toReturn += "\nemboss: "
        for e in emboss:
            toReturn += str(e) + ".. "
        toReturn += "\nScores are "
        for s in scores:
            toReturn += str(int(s)) + " "
        cpe = scores[int((len(scores)+1)/2)]
        toReturn += "\nmedian CPE is " + str(int(cpe)) + " "
        if cpe > 4000:
            score = 0
        else:
            #score = math.log(6000-cpe) * 46.93012749-305.91731341
            score = 119.653*math.exp(-0.001196*cpe)
            if score > 110:
                score = 110
        score = int(score)
        toReturn +="\nResulting score is " + str(score) + "\n"
    except:
        toReturn = "Unexpected error: " + str(sys.exc_info())
    return toReturn
