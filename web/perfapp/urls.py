from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('home/', views.home, name='Home'),
    path('profile/', views.profile, name='Profile'),
    path('profile/update', views.profile_update),
    path('submit/', views.submit, name='Submit'),
    path('login/', auth_views.LoginView.as_view()),
    path('logout/', views.logout_view),
    path('register/', views.register),
    path('scores/', views.score_update)
]
