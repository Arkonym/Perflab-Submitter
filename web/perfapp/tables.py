import django_tables2 as tables
from perfapp.models import Profile, Attempt, Job, Server
from django.contrib.auth.models import User




class ScoreTable(tables.Table):
    class Meta:
        model = User
        sequence = ['id', 'profile.max_score', 'profile.max_score_date', 'last_login']
        fields = ['id', 'profile.max_score', 'profile.max_score_date', 'last_login']
        exclude = ['password', 'email', 'first_name', 'last_name', 'is_staff',
        'is_active', 'is_superuser', 'date_joined']
        attrs= {'class': 'table'}
