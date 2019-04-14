from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from . import views
app_name='perfapp'
urlpatterns = [
    path('home/', views.home, name='Home'),
    path('profile/', views.profile, name='Profile'),
    path('profile/update', views.update_profile),
    path('submit/', views.submit, name='Submit'),
    path('login/', auth_views.LoginView.as_view()),
    path('logout/', views.logout_view),
    path('register/', views.register),
    path('runlab/<int:j_id>', views.progress, name='Progress'),
    path('<int:j_id>/stop/', views.stop_job, name='Stop')
]

urlpatterns +=[
    path('', RedirectView.as_view(url='/home/'))
]
