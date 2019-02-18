from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='Home'),
    path('account/', views.profile, name='Profile')
]
