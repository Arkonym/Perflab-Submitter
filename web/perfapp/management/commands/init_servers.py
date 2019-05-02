from django.core.management.base import BaseCommand
from perfapp.models import Server

import os


class Command(BaseCommand):
    help = 'Run command to initialize all servers in lease file.'

    def _init(self):
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


    def handle(self, *args, **options):
        try:
            self._init()
        except:
            pass
        print("Server list initialized")
