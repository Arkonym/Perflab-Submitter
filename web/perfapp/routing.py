from django.conf.urls import url
from django.urls import path

from . import consumers

websocket_urlpatterns=[
    path('ws/task/<int:job_id>/', consumers.TaskConsumer)
]
