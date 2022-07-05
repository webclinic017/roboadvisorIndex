from django import forms
from django.db import models
from .models import User
from django.forms import ModelForm,Textarea


class UserForm(ModelForm):
	class Meta:
		model=User
		fields = '__all__'