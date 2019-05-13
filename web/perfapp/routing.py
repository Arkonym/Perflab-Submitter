from django.conf.urls import url
from django.urls import path

from . import consumers

websocket_urlpatterns=[
    path('ws/task/<str:job_id>/', consumers.TaskConsumer),
    path('ws/command/<str:user_id>', consumers.CommandConsumer)
]
