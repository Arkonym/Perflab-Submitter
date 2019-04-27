from perfapp.models import Job, Server
import sys,os,subprocess
from subprocess import Popen,PIPE
from redis import Redis
red = Redis(host='redis', port=6379)

def clean_jobs():
    jobs =Job.objects.all()
    for j in jobs:
        j.delete()
    Job.objects.all().delete()


def run():
    clean_jobs()
