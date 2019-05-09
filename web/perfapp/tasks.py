from __future__ import absolute_import
import sys, os, subprocess, django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "perfproject.settings")
django.setup()

from celery import shared_task, task
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded
from celery.signals import worker_ready
from celery_progress.backend import ProgressRecorder
from perfapp.models import Job, Attempt, Server, Error
from django.contrib.auth.models import User

from time import sleep
import datetime
##TEMP IMPORT FOR EXPO##
import random


from subprocess import Popen, PIPE

from redis import Redis
red = Redis(host='redis', port=6379)

logger=get_task_logger(__name__)
@worker_ready.connect
def init(**_):
    print("Server lease check")
    red.set('servers',0)
    try:
        servers = Server.objects.all()
        for serv in servers:
            a="ping -c 1"+ str(serv.ip) + "| grep \"1 received\""
            b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
            b.wait()
            c = b.stdout.read().decode()
            if c == None:
                serv.online= False
            else: red.incr('servers')

        # return "Server lease init completed"
    except:
        return "Server init error. Ensure hardware available on network"

@shared_task
def cleanup():
    try:
        jobs = Job.objects.filter(deletable=True)
        print(jobs)
    except Job.DoesNotExist:
        return "empty jobs"
    for j in jobs:
            #print(str(j.owner) + " : " +str(j))
            j.delete()
    jobs.delete()
    return "cleanup complete"
@shared_task
def jobDeploy():
    ###REMOVE THIS BIT###
    #red.set('servers', 0)
    print("Servers avail: " + red.get('servers').decode())
    if int(red.get('servers')) > 0:
        for user in User.objects.all():
            jobs = Job.objects.filter(owner=user)
            if jobs.exists():
                cur_job = jobs[0]
                if cur_job.status=='New':
                    try:
                        serv = Server.objects.filter(inUse=False)[0]
                        if serv!=None:
                            red.decr('servers')
                            serv.inUse=True
                            serv.uID=request.user.id
                            serv.save()
                        else: raise ValueError("No server avail")
                        #revoke(cur_job.task_id, terminate=True, signal='SIGUSR1')
                        task = runLab.delay(cur_job.jid, user.id, serv)
                        cur_job.task_id = task.task_id
                        cur_job.status = 'Pending'
                        cur_job.save()
                    except:
                        continue
    else:
        for user in User.objects.all():
            jobs = Job.objects.filter(owner=user)
            if jobs.exists():
                cur_job = jobs[0]
                if cur_job.status=='New':
                    task = dummyTask.delay(cur_job.jid, user.id)
                    cur_job.status = 'Pending'
                    cur_job.task_id = task.task_id
                    print(task.task_id)
                    cur_job.save()
    return "Deploy complete"
@shared_task(bind=True)
def placeholder(self):
    ph_recorder = ProgressRecorder(self)
    flag=True
    while(flag!=False):
        try:
            pass
        except SoftTimeLimitExceeded:
            flag=False

@shared_task(bind=True)
def dummyTask(self,j_id, uid):
    progress_recorder = ProgressRecorder(self)
    try:
        user = User.objects.get(id=uid)
        try:
            job = Job.objects.get(owner=user, jid=j_id)
        except Job.DoesNotExist:
            return 'no matching job'
        job.status='RUNNING'
        job.time_started = datetime.datetime.now()
        job.save()
        progress_recorder = ProgressRecorder(self)
        for i in range(100):
            sleep(1)
            progress_recorder.set_progress(i+1, 100)
            if i<10:
                job.cur_action ="Setting Up...\n"
            elif i<20:
                job.cur_action +="Compiling\n"
            elif i<90:
                job.cur_action +="Running\n"
            else:
                job.cur_action +="SCORING\n"
        
        job.status='COMPLETE'
        score = random.randint(70, 95)
        job.cur_action += "Score: " + str(score)
        progress_recorder.set_progress(100,100)
        newAttempt = Attempt(owner=user, note_field=job.note_field, score=score, time_stamp=job.time_created)
        newAttempt.save()
        if job.notefield=='Demo: error':
            new_Err= Error(owner=job.owner, from_job_id=job.jid, errors="Sample Error:\nTest Error")
            new_Err.save()
        job.deletable=True
        job.save()
        return 'task complete'
    except SoftTimeLimitExceeded:
        return 'task aborted'

@shared_task(bind=True)
def runLab(self,j_id,uid, serv):
    try:
        server = serv.ip
        owner = User.objects.get(id=uid)
        try:
            job = Job.objects.get(owner=user, jid=j_id)
            job.status='RUNNING'
            job.hostname = serv.hostname
            job.time_started = datetime.datetime.now()
            job.save()
        except: raise SoftTimeLimitExceeded()
        progress_recorder = ProgressRecorder(self)
        toReturn = ""
        try:
            path = "/home/perfserv/uploads/"+str(uid)+"/"+str(j_id)+"/"
            task_Err = Error(owner=job.owner, from_job_id = job.jid)
            #print path
            config = open("/home" +job.config.path,"r")
            progress_recorder.set_progress(1, 100)

            a="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"rm -rf perflab-setup\""
            b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
            b.wait()
            c = b.stdout.read()
            progress_recorder.set_progress(2, 100)

            a="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"cp -rf perflab-files perflab-setup\""
            b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
            b.wait()
            c = b.stdout.read()
            progress_recorder.set_progress(3, 100)

            f = open(path+"FilterMain.cpp","r")
            for line in f:
                if "unistd" in line:
                    task_Err.err+="Filtermain.cpp:\nIllegal Library unistd\n"
                    task_Err.save()
                    return "Illegal Library unistd"
            a="scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "+path+"FilterMain.cpp perfuser@"+server+":~/perflab-setup/"
            b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
            b.wait()
            c = b.stdout.read()
            progress_recorder.set_progress(4, 100)

            """For each file in config, check illegal lib, then copy to server"""
            for line in config:
            	#print line
                line = line.split()
                if line[1]=="Y":
                    f = open(path+line[0],"r")
                    print (line[0])
                    for line2 in f:
                        if "unistd" in line2:
                            errors.write(line[0] + ": illegal unistd")
                            raise SoftTimeLimitExceeded()
                    a="scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "+path+str(line[0])+" perfuser@"+server+":~/perflab-setup/"
                    print (a)
                    b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
                    b.wait()
                    c = b.stdout.read()
            progress_recorder.set_progress(5, 100)

            a="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"cd perflab-setup/ ; make filter\""
            b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
            b.wait()
            c = b.stdout.read()
            e = b.stderr.read().decode()
            if len(e)>0:
                if "Error" in e:
                    task_Err.errors = "Failed at Make:\n"
                    task_Err+=e
                    task_Err.save()
                    raise SoftTimeLimitExceeded()
                #print e
                if not "ECDSA" in e:
                    task_Err.errors = "Failed at Make:\n"
                    task_Err+=e
                    task_Err.save()
                    raise SoftTimeLimitExceeded()
            #print c
            progress_recorder.set_progress(10, 100)

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

                except:
                    return "gauss " + str(sys.exc_info()) + " " + hostname + " " + str(c) + "\n"+ str(a) + "\n" + str(b.stderr.read())
            job.status="SCORING"
            job.save()
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
        newAttempt = Attempt(owner=user, note_field=job.note_field, score=score, time_stamp=job.time_created)
        newAttempt.save()
        task_Err.delete()
        job.deletable=True
        return toReturn
    except SoftTimeLimitExceeded:
        task_Err.save()
        b.kill()
        a="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"killall -u perfuser;\""
        b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
        print(b.stdout.read())
        serv.inUse=False
        serv.uID=-1
        return "Task Stopped by user"
