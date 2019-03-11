from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class perfsubmission(forms.Form):
    #username = forms.CharField(max_length=50)
    FilterMain = forms.FileField(label='FilterMain.cpp', required=True)
    Filter_c = forms.FileField(label='Filter.cpp',required=False)
    Filter_h = forms.FileField(label='Filter.h',required=False)
    Makefile = forms.FileField(label='Makefile',required=False)
    cs1300_c = forms.FileField(label='cs1300bmp.cpp',required=False)
    cs1300_h = forms.FileField(label='cs1300bmp.h',required=False)

class Registration(UserCreationForm):

    class Meta:
        model=User
        fields=("username", "first_name", "last_name", "email", "password1", "password2")

    def email_validate(self):
        email = self.cleaned_data["email"]
        domain = data.split('@')[1]
        accepted_domains = ["mail.csuchico.edu", "csuchico.edu"]
        if domain not in accepted_domains:
            raise forms.ValidationError("Email must be a valid CSU Chico address")
        return data

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
