from django.core.management.base import BaseCommand
from perfapp.models import Server

import os
from subprocess import Popen, PIPE
from redis import Redis
red = Redis(host='redis', port=6379)

class Command(BaseCommand):
    help = 'Run command to initialize all servers in lease file.'

    def _init(self):
        Server.objects.all().delete()
        Server(ip = '192.168.1.12', hostname = 'rpi2').save()
        Server(ip = '192.168.1.13', hostname = 'rpi3').save()
        Server(ip = '192.168.1.14', hostname = 'rpi4').save()
        Server(ip = '192.168.1.15', hostname = 'rpi5').save()
        Server(ip = '192.168.1.18', hostname = 'rpi8').save()
        Server(ip = '192.168.1.21', hostname = 'rpi11').save()
        Server(ip = '192.168.1.22', hostname = 'rpi12').save()
        Server(ip = '192.168.1.23', hostname = 'rpi13').save()
        Server(ip = '192.168.1.24', hostname = 'rpi14').save()
        Server(ip = '192.168.1.26', hostname = 'rpi16').save()
        Server(ip = '192.168.1.28', hostname = 'rpi18').save()
        Server(ip = '192.168.1.34', hostname = 'rpi24').save()

    def _check(self):
        print("Server lease check")
        red.set('servers',0)
        try:
            servers = Server.objects.all()
            for serv in servers:
                a="ping -c 1"+ str(serv.ip) + "| grep \"1 received\""
                b=Popen(a, shell=True, stdout=PIPE, stderr=PIPE)
                b.wait()
                c = b.stdout.read().decode()
                print(c)
                if c == None:
                    serv.online= False
                else: red.incr('servers')

            # return "Server lease init completed"
        except:
            return "Server init error. Ensure hardware available on network"


    def handle(self, *args, **options):
        try:
            self._init()
            self._check()
        except:
            pass
        print("Server list initialized")
