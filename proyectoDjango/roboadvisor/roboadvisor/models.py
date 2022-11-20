from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.fields.related import OneToOneField
from django.contrib.auth.models import User
from django.utils import timezone
from enum import Enum 
import datetime

class Client(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	is_premium = models.BooleanField(default=False)
	def __str__(self):
		return self.user.username


class Account(models.Model):
	key_id = models.CharField(max_length=200, default=None, unique=True)
	secret_key = models.CharField(max_length=200, default=None, unique=True)
	name=models.CharField(max_length=200, default=None, unique=True)
	balance = models.FloatField()
	totalEquity = models.FloatField()
	user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse("newInvestment_setIndex", kwargs={"pk": self.pk})


class IndexShort(models.Model):
	symbol = models.CharField(max_length=5, default=None)
	def __str__(self):
		return self.symbol

class Index(models.Model):
	symbol = models.CharField(max_length=5, default=None)
	marketCap = models.FloatField(default=0)
	account = models.OneToOneField(Account, on_delete=models.CASCADE)
	def __str__(self):
		return self.symbol


class Stock(models.Model):
	symbol = models.CharField(max_length=5)
	lastPrice = models.FloatField()
	marketCap = models.FloatField()
	actualWeight=models.FloatField(default=0)
	index = models.ForeignKey(Index, on_delete=models.CASCADE, default=None)
	def __str__(self):
		return self.symbol


class Order(models.Model):
	stock = models.ForeignKey(Stock, on_delete=models.CASCADE, default=None)
	quantity = models.FloatField()
	date = models.DateField(default=timezone.now)
	price = models.FloatField(default=0)
	def __str__(self):
		return self.stock.symbol + ", " + str(self.quantity)



class Purchase(models.Model):
	id = models.CharField(primary_key= True, max_length=100)
	status = models.CharField(max_length=100)
	codeStatus = models.CharField(max_length=100)
	totalPurchase = models.DecimalField(max_digits=5 ,decimal_places= 2)
	nameClient = models.CharField(max_length=100)
	lastNameClient = models.CharField(max_length=100)
	emailClient = models.EmailField(max_length=100)
	adressClient = models.CharField(max_length=100)
	date = models.DateField(default=timezone.now)
	client = OneToOneField(Client, on_delete=models.CASCADE, default=None)

	def __str__(self):
		return self.nameCliente


class UploadFile(models.Model):
	file=models.FileField()