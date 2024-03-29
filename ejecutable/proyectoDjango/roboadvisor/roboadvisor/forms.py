from django import forms
from django.db import models
from .models import *
from django.forms import ModelForm,Textarea
import alpaca_trade_api as tradeapi
import os


class AccountForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ('name', 'key_id', 'secret_key',)

class UploadFileForm(forms.Form):
    file = forms.FileField()