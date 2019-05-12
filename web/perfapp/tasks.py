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
from django.db.models import Q

from time import sleep
import datetime
import math
##TEMP IMPORT FOR EXPO##
import random

from channels.layers import get_channel_layer
from asgiref.sync import AsyncToSync as AtoS


from subprocess import Popen, PIPE

from redis import Redis
red = Redis(host='redis', port=6379)

logger=get_task_logger(__name__)

@shared_task
def init():
    print("Server lease check")
    red.set('servers',0)
    try:
        servers = Server.objects.all()
        for serv in servers:
            a="ping -c 1 "+ str(serv.ip) + "| grep \"1 received\""
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
    layer = get_channel_layer()
    print("Servers avail: " + red.get('servers').decode())
    if int(red.get('servers')) > 0:
        for user in User.objects.all():
            jobs = Job.objects.filter(owner=user)
            if jobs.exists():
                running = jobs.filter(Q(status='RUNNING') | Q(status='SCORING') | Q(status='In Queue'))
                if running.exists():
                    continue
                else:
                    pending = jobs.filter(status='Pending')
                    #print(pending)
                    if pending.exists():
                        try:
                            cur_job = pending[0]
                            #print(cur_job)
                            serv = Server.objects.filter(online=True, inUse=False)[0]
                            #print(serv)
                            if serv!=None:
                                #print("Server not none")
                                red.decr('servers')
                                serv.inUse=True
                                serv.uID=user.id
                                serv.save()
                            else:
                                raise ValueError("No server avail")
                            if cur_job.note_field.split(' ', 1)[0] == "Demo":
                                task= dummyTask.delay(cur_job.jid, user.id)
                            else:
                                #print("runLab sent")
                                task = runLab.delay(cur_job.jid, user.id, serv.id)
                            msg = {'type': 'task_message', 'status': 'In Queue', 'action': 'Waiting', 'task_id': task.task_id}
                            AtoS(layer.group_send)(str(job_id), msg)
                            cur_job.status = "In Queue"
                            cur_job.task_id = task.task_id
                            cur_job.save()
                        except Exception as e:
                            print(e)
                            continue
    else:
        for user in User.objects.all():
            jobs = Job.objects.filter(owner=user)
            if jobs.exists():
                running = jobs.filter(status='RUNNING')
                if running.exists():
                    continue
                else:
                    pending = jobs.filter(status='Pending')
                    if pending.exists():
                        cur_job=pending[0]
                        task = dummyTask.delay(cur_job.jid, user.id)
                        cur_job.task_id = task.task_id
                        print(task.task_id)
                        cur_job.save()
    return "Deploy complete"



@shared_task(bind=True)
def dummyTask(self,j_id, uid):
    progress_recorder = ProgressRecorder(self)
    layer = get_channel_layer()
    try:
        user = User.objects.get(id=uid)
        try:
            job = Job.objects.get(owner=user, jid=j_id)
        except Job.DoesNotExist:
            return 'no matching job'
        task_id = self.request.id
        msg = {'type': 'task_message', 'status': 'RUNNING', 'action':'setting up', 'task_id': task_id}
        print("Sending message on channel " + str(job.id))
        AtoS(layer.group_send)(str(job.id), msg)
        job.status='RUNNING'
        job.time_started = datetime.datetime.now()
        job.save()
        progress_recorder = ProgressRecorder(self)
        for i in range(100):
            sleep(1)
            progress_recorder.set_progress(i+1, 100)
            if i<10:
                msg['action'] ="Setting Up..."
            elif i<=20:
                msg['action'] ="Compiling..."
            elif i<90:
                msg['action'] ="Running"
            else:
                msg['action'] ="SCORING"
            AtoS(layer.group_send)(str(job.id), msg)

        score = random.randint(70, 95)

        job.status="COMPLETE \nScore: " + str(score)
        job.cur_action = "Score: " + str(score)
        job.save()

        msg['action'] = "Score: " + str(score)
        msg['status'] = "COMPLETE \nScore: " + str(score)
        AtoS(layer.group_send)(str(job.id), msg)

        progress_recorder.set_progress(100,100)
        newAttempt = Attempt(owner=user, note_field=job.note_field, score=score, time_stamp=job.time_created)
        newAttempt.result_out = "Demo score is: " + str(score)
        newAttempt.save()
        if job.note_field=='Demo error':
            new_Err= Error(owner=job.owner, from_job_id=job.jid, errors="Sample Error:\nTest Error")
            new_Err.save()
        job.deletable=True
        job.save()
        return 'task complete'
    except SoftTimeLimitExceeded:
        return 'task aborted'
    except Exception as e:
        print(e)

@shared_task(bind=True)
def runLab(self,j_id,uid, serv_id):
    try:
        serv = Server.objects.get(id=serv_id)
        server = serv.ip
        user = User.objects.get(id=uid)
        job_not_found=False
        task_Err = Error(owner=user, from_job_id = j_id, errors="")
        error_flag=False
        b=None
        layer = get_channel_layer()
        try:
            job = Job.objects.get(owner=user, jid=j_id)
            job.status='RUNNING'
            job.hostname = serv.hostname
            job.task_id = self.request.id
            job.time_started = datetime.datetime.now()
            job.save()
        except Job.DoesNotExist:
            print("Job not found")
            job_not_found = True
            task_Err.errors+="Job not found"
            error_flag=True
            raise SoftTimeLimitExceeded()
        progress_recorder = ProgressRecorder(self)
        msg = {'type': 'task_message', 'status': 'RUNNING', 'action':'Setting Up', 'task_id': self.request.id}

        toReturn = ""
        try:
            path = "/home/perfserv/uploads/"+str(uid)+"/"+str(j_id)+"/"

            #print path
            config = open(path+"/config.txt","r")
            AtoS(layer.group_send)(str(job.id), msg)
            progress_recorder.set_progress(1, 100)
            # job.cur_action = "Setting Up"
            # job.save()

            a="ssh -i /home/perfserv/.ssh/id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"rm -rf perflab-setup\""
            b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
            b.wait()
            c = b.stdout.read()
            e = b.stderr.read().decode()
            progress_recorder.set_progress(2, 100)

            a="ssh -i /home/perfserv/.ssh/id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"cp -rf perflab-files perflab-setup\""
            b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
            b.wait()
            c = b.stdout.read()
            progress_recorder.set_progress(3, 100)
            msg['action'] = "Scanning FilterMain"
            AtoS(layer.group_send)(str(job.id), msg)
            # job.cur_action = "Scanning FilterMain"
            # job.save()

            f = open(path+"FilterMain.cpp","r")
            for line in f:
                if "unistd" in line:
                    task_Err.err+="Filtermain.cpp:\nIllegal Library unistd\n"
                    task_Err.save()
                    error_flag=True
            if error_flag==False:
                a="scp -i /home/perfserv/.ssh/id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "+path+"FilterMain.cpp perfuser@"+server+":~/perflab-setup/"
                b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
                b.wait()
                c = b.stdout.read()
            progress_recorder.set_progress(4, 100)
            msg['action'] = "Sending Files"
            AtoS(layer.group_send)(str(job.id), msg)
            # job.cur_action = "Sending Files"
            # job.save()
            """For each file in config, check illegal lib, then copy to server"""

            for line in config:
            	#print line
                line = line.split()
                if line[1]=="Y":
                    f = open(path+line[0],"r")
                    print (line[0])
                    for line2 in f:
                        if "unistd" in line2:
                            task_Err.errors+=(line[0] + ": illegal unistd\n")
                            task_Err.save()
                            error_flag=True
                    if error_flag==False:
                        a="scp -i /home/perfserv/.ssh/id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "+path+str(line[0])+" perfuser@"+server+":~/perflab-setup/"
                        print (a)
                        b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
                        b.wait()
                        c = b.stdout.read()
            if error_flag==True:
                job.status="ERROR"
                task_Err.save()
                raise SoftTimeLimitExceeded()
            progress_recorder.set_progress(5, 100)
            msg['action'] = "Compiling..."
            AtoS(layer.group_send)(str(job.id), msg)
            # job.cur_action = "Compiling..."
            # job.save()

            a="ssh -i /home/perfserv/.ssh/id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"cd perflab-setup/ ; make filter\""
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
            msg['action'] = "Running Gauss"
            AtoS(layer.group_send)(str(job.id), msg)
            # job.cur_action = "Running Gauss"
            # job.save()

            status = 10.0
            tests = 5
            increment = (100.0-status)/(4.0*float(tests))
            scores = []
            #GAUSS
            gauss = []
            count = 0
            while count < tests:
                a="ssh -i /home/perfserv/.ssh/id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"cd perflab-setup/ ; ./gauss.sh\""
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
                     task_Err.errors+="Gauss:\n " + str(sys.exc_info()) + " " + serv.hostname + " " + str(c) + "\n"+ str(a) + "\n" + str(b.stderr.read()) + "\n"
                     task_Err.save()
                     raise SoftTimeLimitExceeded()
            msg['action'] = "Running Avg"
            AtoS(layer.group_send)(str(job.id), msg)
            # job.cur_action = "Running Avg"
            # job.save()
            #AVG
            count = 0
            avg = []
            while count < tests:
                a="ssh -i /home/perfserv/.ssh/id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"cd perflab-setup/ ; ./avg.sh\""
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
                        progress_recorder.set_progress(status, 100)

                except:
                    task_Err.errors+="Avg:\n " + str(sys.exc_info()) + " " + serv.hostname + " " + str(c) + "\n"+ str(a) + "\n" + str(b.stderr.read()) + "\n"
                    task_Err.save()
                    raise SoftTimeLimitExceeded()
            msg['action'] = "Running HLine"
            AtoS(layer.group_send)(str(job.id), msg)
            # job.cur_action = "Running HLine"
            # job.save()
            #HLINE
            count = 0
            hline = []
            while count < tests:
                a="ssh -i /home/perfserv/.ssh/id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"cd perflab-setup/ ; ./hline.sh\""
                b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
                b.wait()
                c = b.stdout.read()
                e = b.stderr.read().decode()
                line = c.split()
                try:
                    score = float(line[-1])
                    if not score > 9000 and not score <=0: # Check for and ignore odd scores
                        scores = scores + [score]
                        hline = hline + [score]
                        status = status + increment
                        count = count + 1
                        progress_recorder.set_progress(status, 100)

                except:
                    task_Err.errors+="Hline:\n " + str(sys.exc_info()) + " " + serv.hostname + " " + str(c) + "\n"+ str(a) + "\n" + str(b.stderr.read()) + "\n"
                    task_Err.save()
                    error_flag=True
                    raise SoftTimeLimitExceeded()
            msg['action'] = "Running Emboss"
            AtoS(layer.group_send)(str(job.id), msg)
            # job.cur_action = "Running Emboss"
            # job.save()
            #EMBOSS
            count = 0
            emboss = []
            while count < tests:
                a="ssh -i /home/perfserv/.ssh/id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"cd perflab-setup/ ; ./emboss.sh\""
                b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
                b.wait()
                c = b.stdout.read().decode()

                line = c.split()
                #print c
                try:
                    score = float(line[-1])
                    if not score > 9000 and not score <=0: # Check for and ignore odd scores
                        scores = scores + [score]
                        emboss = emboss + [score]
                        status = status + increment
                        count = count + 1
                        progress_recorder.set_progress(status, 100)

                except:
                    #print e
                    task_Err.errors+=  "emboss " + str(sys.exc_info()) + " " + serv.hostname + "\n"
                    task_Err.save()
                    error_flag=True
                    raise SoftTimeLimitExceeded()

            scores.sort()
            #print scores
            msg['status'] = "SCORING"
            msg['action'] = "Running HLine"
            AtoS(layer.group_send)(str(job.id), msg)
            job.status="SCORING"
            job.cur_action="Moving numbers around..."
            job.save()
            toReturn += "gauss:\n"
            for g in gauss:
                toReturn += str(g) + "..\n "
            toReturn += "\navg:\n"
            for a in avg:
                toReturn += str(a) + "..\n "
            toReturn += "\nhline:\n"
            for h in hline:
                toReturn += str(h) + "..\n "
            toReturn += "\nemboss:\n"
            for e in emboss:
                toReturn += str(e) + "..\n "
            toReturn += "\nScores are:\n"
            count = 0
            for s in scores:
                if count < 4:
                    toReturn += str(int(s)) + " "
                    count+=1
                else:
                    toReturn += str(int(s)) + "\n"
                    count = 0
            cpe = scores[int((len(scores)+1)/2)]
            toReturn += "\nmedian CPE is " + str(int(cpe)) + "\n"
            if cpe > 4000:
                score = 0
            else:
                #score = math.log(6000-cpe) * 46.93012749-305.91731341
                score = 119.653*math.exp(-0.001196*cpe)
                if score > 110:
                    score = 110
            score = int(score)
            toReturn+="\nResulting score is " + str(score)

            msg['status'] = "COMPLETE \nScore: " + str(score)
            msg['action'] = "Score:" + str(score)
            AtoS(layer.group_send)(str(job.id), msg)

            job.status="COMPLETE \nScore: " + str(score)
            job.cur_action = "Score:" + str(score)
            job.save()
        except:
            task_Err.errors += "\nUnexpected error: " + str(sys.exc_info())
            task_Err.save()
            error_flag=True
            raise SoftTimeLimitExceeded()
        newAttempt = Attempt(owner=user, note_field=job.note_field, score=score, result_out = toReturn, time_stamp=job.time_created)
        newAttempt.save()
        if task_Err.id!=None:
            task_Err.delete()
        job.deletable=True
        job.save()
        red.incr('server')
        progress_recorder.set_progress(100, 100)
        return "runLab Completed successfully"
    except SoftTimeLimitExceeded:
        if error_flag==True:
            err_block = task_Err.errors
            task_Err.errors = "A team of flying monkies has been dispatched. When they show up (eventually), show them this log.\n"
            task_Err.errors+=err_block
            task_Err.save()
            job.cur_action= "ERROR"
            job.status= "ERROR"
            job.save()
            msg['status'] = "ERROR"
            msg['action'] = err_block
            AtoS(layer.group_send)(str(job.id), msg)
        if b!=None:
            b.kill()
        a="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"killall -u perfuser;\""
        b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
        b.wait()
        if job_not_found==False:
            job.deletable=True
            job.save()
        #print(b.stdout.read())
        serv.inUse=False
        serv.uID=-1
        red.incr('server')
        if error_flag:
            self.update_state(state='FAILURE')
            return "Task failed with errors"
        else:
            return "Task Stopped by user"
    except Exception as e:
        print(e)
