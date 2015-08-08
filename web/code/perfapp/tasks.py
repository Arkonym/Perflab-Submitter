from celery import task

from time import sleep
import math

from redis import Redis
red = Redis(host='redis2', port=6379)
#import sys,os,subprocess
#from subprocess import Popen,PIPE

@task
def testing(count):
    #print "hello"
    for i in range(5):
        sleep(1)
    #print "done with task"
    red.incr('servers')
    return count