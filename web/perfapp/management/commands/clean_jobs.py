from django.core.management.base import BaseCommand
from perfapp.models import Job, Server

import os

class Command(BaseCommand):
    help = 'Run command to delete all jobs and their associated files.'

    def _clean_jobs(self):
        jobs =Job.objects.all()
        for j in jobs:
            j.delete()
        Job.objects.all().delete()


    def handle(self, *args, **options):
        try:
            self._clean_jobs()
        except:
            pass
        print("Old jobs and files cleaned")
