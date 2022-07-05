from django.db import models
from django.db.models.fields.related import OneToOneField
from django.utils import timezone


class User(models.Model):
	username = models.CharField(max_length=20)
	keyId = models.CharField(max_length=50, default=None)
	secretKey = models.CharField(max_length=50, default=None)
	def __str__(self):
		return self.username


class Account(models.Model):
	balance = models.FloatField()
	totalEquity = models.FloatField()
	def __str__(self):
		return self.balance


class Index(models.Model):
	symbol = models.CharField(max_length=5, default=None)
	marketCap = models.FloatField()
	equity = models.FloatField()
	def __str__(self):
		return self.symbol


class Stock(models.Model):
	symbol = models.CharField(max_length=5)
	date = models.DateField(default=timezone.now)
	price = models.FloatField()
	marketCap = models.FloatField()
	index = models.ForeignKey(Index, on_delete=models.CASCADE, default=None)
	def __str__(self):
		return self.symbol


class Order(models.Model):
	stock = OneToOneField(Stock, on_delete=models.CASCADE)
	quantity = models.FloatField()
	def __str__(self):
		return self.stock + self.quantity