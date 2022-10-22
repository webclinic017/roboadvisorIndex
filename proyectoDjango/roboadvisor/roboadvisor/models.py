from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.fields.related import OneToOneField
from django.utils import timezone
from enum import Enum 
import datetime


class MyUserManager(BaseUserManager):
	use_in_migrations = True
	
	# python manage.py createsuperuser
	def create_superuser(self, email, is_staff, password):
		user = self.model(
						  email = email,                         
						  is_staff = is_staff,
						  )
		user.set_password(password)
		user.save(using=self._db)
		return user

class UserModel(AbstractBaseUser):
	sys_id = models.AutoField(primary_key=True, blank=True)        
	email = models.EmailField(max_length=127, unique=True, null=False, blank=False)
	is_staff = models.BooleanField(default=True)
	is_active = models.BooleanField(default=True)
	is_premium = models.BooleanField(default=False)
	
	objects = MyUserManager()

	USERNAME_FIELD = "email"
	# REQUIRED_FIELDS must contain all required fields on your User model, 
	# but should not contain the USERNAME_FIELD or password as these fields will always be prompted for.
	REQUIRED_FIELDS = ['is_staff']

	class Meta:
		app_label = "roboadvisor"
		db_table = "user"

	def __str__(self):
		return self.email

	def get_full_name(self):
		return self.email

	def get_short_name(self):
		return self.email


	# this methods are require to login super user from admin panel
	def has_perm(self, perm, obj=None):
		return self.is_staff

	# this methods are require to login super user from admin panel
	def has_module_perms(self, app_label):
		return self.is_staff


#PLANS = (
	#('F', 'Free'),
	#('P', 'Premium'),
#)


class Account(models.Model):
	key_id = models.CharField(max_length=200, default=None, unique=True)
	secret_key = models.CharField(max_length=200, default=None, unique=True)
	name=models.CharField(max_length=200, default=None, unique=True)
	balance = models.FloatField()
	totalEquity = models.FloatField()
	user = models.ForeignKey(UserModel, on_delete=models.CASCADE, default=None)
	#user = OneToOneField(UserModel, on_delete=models.CASCADE)
	#plan = models.CharField(max_length=1, choices=PLANS, default='F')
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
	#account = models.ForeignKey(Account, on_delete=models.CASCADE, default=None)
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
	stock = OneToOneField(Stock, on_delete=models.CASCADE)
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
    user = OneToOneField(UserModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.nameCliente