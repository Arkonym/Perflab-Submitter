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
    path('runlab/<int:t_id>', views.progress, name='Progress'),
    path('<int:j_id>/stop/', views.stop_job, name='Stop'),
    path('<int:j_id>/cancel/', views.cancel_job, name='Cancel'),
    path('<int:e_id>/delete_err/', views.clear_error, name='Delete'),
    path('<int:a_id>/delete_att/', views.clear_attempt, name='Delete_Att'),
    path('clear_att/', views.clear_all_attempts, name="Clear_All_Att"),
    path('clear_q/', views.clear_user_queue),
    path('clear_err/', views.clear_all_errs, name="Clear_All_Errs"),
    path('task_poll/stat/<int:id>', views.task_status_poll, name='status'),
    path('task_poll/act/<int:id>', views.task_action_poll, name='action')
]

urlpatterns +=[
    path('', RedirectView.as_view(url='/home/'))
]
