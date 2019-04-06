from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('home/', views.home, name='Home'),
    path('profile/<int:user_id>', views.profile, name='Profile'),
    path('profile/<int:user_id>/update', views.update_profile),
    path('submit/', views.submit, name='Submit'),
    path('login/', auth_views.LoginView.as_view()),
    path('logout/', views.logout_view),
    path('register/', views.register),
    path('scores/', views.score_update)
]

urlpatterns +=[
    path('', RedirectView.as_view(url='/home/'))
]
