from __future__ import absolute_import
import sys, os, subprocess, django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "perfproject.settings")
django.setup()

from celery import shared_task, task
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded
from celery_progress.backend import ProgressRecorder
from perfapp.models import Job, Attempt, Server
from django.contrib.auth.models import User

from time import sleep

from subprocess import Popen, PIPE

from redis import Redis
red = Redis(host='redis', port=6379)

logger=get_task_logger(__name__)

@worker_ready.connect
def init_servers():
    try:
        red.set('servers',0)
        Server.objects.all().delete()
        initial = 11
        for lease in range(24):
          a="ssh -i /home/perfserv/.ssh/id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@192.168.1."+str(initial+lease)+ " \"cat /proc/modules | grep aprofile\""
          print a
          b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
          b.wait()
          c = b.stdout.read()
          print b.stderr.read()
          print c
          if "aprofile" in c:
              print c
              red.incr('servers')
              ip = "192.168.1."+str(initial+lease)
              print ip
              entry = servers(ip=ip, hostname="rpi"+str(lease+1))
              entry.save()
        return "Server lease init completed"
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

@shared_task(bind=True)
def dummyTask(self,j_id, uid):
    try:
        user = User.objects.get(id=uid)
        try:
            job = Job.objects.get(owner=user, jid=j_id)
        except Job.DoesNotExist:
            return 'no matching job'
        job.status='RUNNING'
        job.save()
        progress_recorder = ProgressRecorder(self)
        for i in range(100):
            sleep(1)
            progress_recorder.set_progress(i+1, 100)
            job.percent_complete=i+1
            job.save()
        job.status='COMPLETE'
        progress_recorder.set_progress(100,100)
        newAttempt = Attempt(owner=user, note_field=job.note_field, score=89.99, time_stamp=job.time_created)
        newAttempt.save()
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
        job = Job.objects.get(owner=user, jid=j_id)
        job.status='RUNNING'
        job.save()
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
        newAttempt = Attempt(owner=user, note_field=job.note_field, score=score, time_stamp=job.time_created)
        newAttempt.save()
        return toReturn
    except SoftTimeLimitExceeded:
        b.kill()
        a="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no perfuser@"+server+ " \"killall -u perfuser;\""
        b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
        return "Task Stopped by user"
