from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

#from .forms import UserForm
#from .models import User
from .forms import AccountForm
#from .models import UserModel
from .models import Client
from .models import Account
from .models import Index
from .models import IndexShort
from .models import Stock
from .models import Order
from .models import Purchase
import logging
import os
import pandas as pd
import requests
import alpaca_trade_api as tradeapi
import math
import yfinance as yf
from datetime import datetime
import time
import pandas_datareader as web
import logging
from django.contrib import messages
from django.shortcuts import get_object_or_404
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersGetRequest, OrdersCaptureRequest
import sys, json
import finnhub
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#class MyAuthBackend(object):
#	def authenticate(self, email, password):    
#		try:
#			user = UserModel.objects.get(email=email)
#			if user.check_password(password):
#				return user
#			else:
#				return None
#		except UserModel.DoesNotExist:
#			logging.getLogger("error_logger").error("user with login %s does not exists " % login)
#			return None
#		except Exception as e:
#			logging.getLogger("error_logger").error(repr(e))
#			return None

#	def get_user(self, user_id):
#		try:
#			user = UserModel.objects.get(sys_id=user_id)
#			if user.is_active:
#				return user
#			return None
#		except UserModel.DoesNotExist:
#			logging.getLogger("error_logger").error("user with %(user_id)d not found")
#			return None

def signupView(request):
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user=form.save()
			Client.objects.create(is_premium=False, user_id=user.id)
			login(request,user)
			return redirect("/home")
	else:
		form = UserCreationForm()
	context = {"form": form}
	return render(request, 'signup.html', context)

def loginView(request):
	if request.method == "POST":
		form = AuthenticationForm(data=request.POST)
		if form.is_valid():
			user=form.get_user()
			login(request,user)
			return redirect("/home")
	else:
		form = AuthenticationForm()
	context = {"form": form}
	return render(request, 'login.html', context)


def logoutView(request):
	if request.method == "POST":
		logout(request)
		return redirect("/home")


def base(request):
	user = request.user
	print(user.is_authenticated)
	context = {"user": user}
	return render(request, 'base.html', context)

def home(request):
	user = request.user
	context = {"user": user}
	return render(request, 'home.html', context)

def manageAccount(request):
	user = request.user
	user_id = user.id
	accounts = Account.objects.filter(user_id=user_id)
	context = {"accounts": accounts}
	return render(request, 'manageAccount.html', context)

@login_required
def newInvestment_setAccount(request):
	selected_index = None
	user = request.user
	user_id = user.id
	query = Account.objects.filter(user_id=user_id)
	queryBool = query.exists()
	account=None
	key_id=None
	secret_key=None


	results = IndexShort.objects.all()

	if request.method == "POST":
		if 'alpacaCredentials' in request.POST:
			form = AccountForm(request.POST)
			if form.is_valid():
				try:
					api = tradeapi.REST(request.POST.get('key_id'), request.POST.get('secret_key'), "https://paper-api.alpaca.markets", api_version='v2')
					alpacaAccount = api.get_account()
					account = form.save(commit=False)
					account.user = request.user
					account.balance = alpacaAccount.equity
					account.totalEquity = alpacaAccount.equity
					account.save()
					context = {"account": account, "alpacaAccount": alpacaAccount}
					return redirect("/newInvestment_setIndex/"+str(account.pk))
					return render(request, 'newInvestment_setIndex.html')
				except Exception as e:
					#logger.exception('Error with: '+ str(e))
					form = AccountForm()
					messages.add_message(request, messages.ERROR, "Credentials already in use or wrong. Please use the credentials of a new Alpaca account.")
					context = {"form": form, "results": results, "queryBool": queryBool}
					return render(request, 'newInvestment_setAccount.html', context)

					#return HttpResponseRedirect('manageAccount.html')  

	else:
		form = AccountForm()
		context = {"form": form, "results": results, "queryBool": queryBool}
		return render(request, 'newInvestment_setAccount.html', context)
		
		
@login_required
def newInvestment_setIndex(request, pk):

	selected_index = None
	user = request.user
	user_id = user.id

	account= get_object_or_404(Account, pk=pk)

	results = IndexShort.objects.all()

	directorio = "C:/Users/Josema/Desktop/TFG/Datos/"

	finnhub_client = finnhub.Client(api_key="cci63qiad3ibcn4bhk6g")

	comissionPerBuy=0.01

	contadorT=0
	contadorY=0

	iteraciones=115
	cont=0

	ind = Index.objects.filter(account_id= account.id)
	print(ind)
	booInd = ind.exists()
	print(booInd)

	if request.method == "POST":
		if 'newInvestment_setIndex' in request.POST:
			try:
				selected_index = request.POST.get("index")
				#indexShort =  IndexShort.objects.get(symbol=selected_index)
				df =pd.read_csv(directorio+selected_index+'.csv')
				#I = Index.objects.create(symbol=selected_index, marketCap='0', account=account)
				all_symbols = df['Symbol']
				symbols = []
				market_caps = []
				prices = []
				actual_weights = []

				total_market_cap = 0

				tabla = pd.DataFrame(columns = ['Symbol', 'MarketCap', 'Price', 'Weight'])

				if user.client.is_premium is False:
					for item in all_symbols:
						try:
							symbol=item.replace('.', '-', 1)

							ticker_yahoo = yf.Ticker(symbol)
							data = ticker_yahoo.history()
							price = data['Close'].iloc[-1]
							marketCap=web.get_quote_yahoo(symbol)['marketCap'][0]
							

							symbols.append(symbol)
							prices.append(price)
							market_caps.append(marketCap)

						except Exception as e:
							messages.add_message(request, messages.ERROR, "Error with: "+ symbol + str(e))
				else:
					for item in all_symbols:
						if contadorY>=iteraciones and contadorT<60:
							time.sleep(61-contadorT)
							contadorT=0
							contadorY=0
	
						if contadorY<iteraciones:
							try: 
								symbol=item.replace('.', '-', 1)
									
								instanteInicial = time.time()
									
								last_quote = finnhub_client.quote(symbol)['c']
								marketCap=finnhub_client.company_profile2(symbol=symbol)['marketCapitalization']
									
								instanteFinal = time.time()
								tiempo = instanteFinal - instanteInicial
									
								contadorY=contadorY+2
									
								contadorT=contadorT+tiempo

								symbols.append(symbol)
								prices.append(last_quote)
								market_caps.append(marketCap)
									
							except Exception as e:
								#time.sleep(35)
								messages.add_message(request, messages.ERROR, "Error with: "+ symbol + str(e))
				
				total_market_cap = sum(market_caps)

				I = Index.objects.create(symbol=selected_index, marketCap=total_market_cap, account=account)

				tabla['Symbol'] = symbols
				tabla['MarketCap'] = market_caps
				tabla['Price'] = prices

				for item in market_caps:
					actual_weights.append(item/total_market_cap*100)
		
				tabla['Weight'] = actual_weights

				for i in tabla.index:
					cl=(tabla['Weight'][i]*account.totalEquity/100)/(tabla['Price'][i]+tabla['Price'][i]*comissionPerBuy)
					

					alpaca = tradeapi.REST(account.key_id,
										account.secret_key,
										'https://paper-api.alpaca.markets')

					apiV2 = tradeapi.REST(account.key_id, account.secret_key, 'https://paper-api.alpaca.markets', api_version='v2')

					asset = apiV2.get_asset(tabla['Symbol'][i])
					if asset.fractionable and cl>0:
						alpaca.submit_order(
						symbol=tabla['Symbol'][i],
						qty=cl,
						side="buy",
						type="market",
						time_in_force='day')
						cont=cont+(cl*tabla['Price'][i])
						O = Order.objects.create(stock=Stock.objects.create(symbol=tabla['Symbol'][i], lastPrice=tabla['Price'][i], marketCap=tabla['MarketCap'][i], actualWeight=tabla['Weight'][i], index=I), quantity=cl, price=tabla['Price'][i])

					if not asset.fractionable and math.floor(cl)>0:
						alpaca.submit_order(
						symbol=tabla['Symbol'][i],
						qty=math.floor(cl),
						side="buy",
						type="market",
						time_in_force='day')
						cont=cont+(cl*tabla['Price'][i])
						O = Order.objects.create(stock=Stock.objects.create(symbol=tabla['Symbol'][i], lastPrice=tabla['Price'][i], marketCap=tabla['MarketCap'][i], actualWeight=tabla['Weight'][i], index=I), quantity=cl, price=tabla['Price'][i])

				#context = {"results": results, "account":account}
				#return render(request, 'manageAccount.html')
				#return redirect("/manageAccount/")
				print(cont)
				
				return HttpResponseRedirect("/manageAccount/")
					#S = Stock.objects.create(symbol=tabla['Symbol'][i], price=tabla['Price'][i], marketCap=tabla['MarketCap'][i], actualWeight=tabla['Weight'][i], index=I)
			except Exception as e:
				#logger.exception('Error with: '+ str(e))
				messages.add_message(request, messages.ERROR, "This account already has an assigned index." + str(e))
				form = AccountForm()
				context = {"form": form, "results": results, "account":account}
				
				return redirect("/newInvestment_setIndex/"+str(pk))
				return render(request, 'newInvestment_setIndex.html', context)

	else:
		form = AccountForm()
		context = {"form": form, "results": results, "account":account, "booInd": booInd}
		return render(request, 'newInvestment_setIndex.html', context)

@login_required
def showAccount(request, pk):
	user = request.user
	user_id = user.id
	ind = Index.objects.get(account_id=pk)
	stocks = Stock.objects.filter(index_id=ind.id)
	orders = []
	for s in stocks:
		orders.append(Order.objects.get(stock_id=s.id))

	context = {"orders": orders}
	return render(request, 'showAccount.html' , context)

@login_required
def loadIndexesData(request):
	directorio = "C:/Users/Josema/Desktop/TFG/Datos"
	list=[]
	user = request.user
	user_id = user.id
	query = Account.objects.filter(user_id=user_id).values()
	queryBool = query.exists()
	results = IndexShort.objects.all()
	list2=[]
	for i in results:
		list2.append(i.symbol)

	with os.scandir(directorio) as ficheros:
		for fichero in ficheros:
			list.append(fichero.name[0:-4])

		for i in list:
			print(queryBool)
			if i not in list2:
				I = IndexShort.objects.create(symbol=i)

@login_required
def loadIndexes(request, pk):

	if request.method=='POST':     
		d = loadIndexesData(request)
		return redirect("/newInvestment_setIndex/"+str(pk))
		return render(request, 'newInvestment_setIndex.html')
	else:
		return redirect("/newInvestment_setIndex/"+str(pk))

@login_required
def listIndexes(request):
	results = IndexShort.objects.all()
	return render(request, 'manageAccount.html',{'results':results})


@login_required
def rebalanceAll(request):
	user = request.user
	user_id = user.id

	account= get_object_or_404(Account, pk=pk)
	index = Index.objects.get(Account, pk=pk)

	results = IndexShort.objects.all()

@login_required
def rebalanceIndex(pk):
	index = Index.objects.get(Account, pk=pk)

@login_required
def checkout(request):
	user = request.user
	user_id = user.id
	boo = user.client.is_premium

	try:
		if user.client.is_premium is not True:
			context = {"boo":boo}
			return render(request, 'checkout.html', context)

		else:
			raise Exception()

	except Exception as e:
		logger.exception('Error with: '+ str(e))
		messages.add_message(request, messages.ERROR, "You already have an active subscription.")
		context = {"boo":boo}
		return render(request, 'checkout.html', context)

@login_required
def pricing(request):
	user = request.user
	context = {"user": user}
	return render(request, 'pricing.html', context)


def payment(request):
	try:
		user = request.user
		user_id = user.id

		data = json.loads(request.body)
		order_id = data['orderID']

		detail = GetOrder().get_order(order_id)
		detailPrice = float(detail.result.purchase_units[0].amount.value)

		if detailPrice == 10:
			trx = CaptureOrder().capture_order(order_id, debug=True)
			purchase = Purchase.objects.create(
				id= trx.result.id, 
				status= trx.result.status, 
				codeStatus= trx.status_code, 
				totalPurchase = trx.result.purchase_units[0].payments.captures[0].amount.value, 
				nameClient= trx.result.payer.name.given_name, 
				lastNameClient= trx.result.payer.name.surname, 
				emailClient= trx.result.payer.email_address, 
				adressClient= trx.result.purchase_units[0].shipping.address.address_line_1,
				client=user.client)
			purchase.save()

			Client.objects.filter(user_id=user_id).update(is_premium=True)

			data = {
				"message": "=D"
			}
			return JsonResponse(data)
		else:
			data = {
				"message": "Error =("
			}
			return JsonResponse(data)
	except Exception as e:
		logger.exception('Error with: '+ str(e))
		messages.add_message(request, messages.ERROR, "You already have an active subscription.")
		return render(request, 'checkout.html')


	#return HttpResponse('<script type="text/javascript">window.close()</script>')
	#return HttpResponseRedirect("/manageAccount")


class PayPalClient:
	def __init__(self):
		self.client_id = "AfybVsJRqglGTuupYnqdikucM52W-yLrm8H5WdOoJvwyLz1oz0UjukPcusLTy8BenJgQ_bL9OVxxjkFe"
		self.client_secret = "EA111C76kHQiKGyECS4fwDv7rjzivmpdc3Z9GoRwIQOsaEBypYmdGT-6xc5iYqI_uUhLXmLsrzgbBHZR"

		"""Set up and return PayPal Python SDK environment with PayPal access credentials.
			 This sample uses SandboxEnvironment. In production, use LiveEnvironment."""

		self.environment = SandboxEnvironment(client_id=self.client_id, client_secret=self.client_secret)

		""" Returns PayPal HTTP client instance with environment that has access
			credentials context. Use this instance to invoke PayPal APIs, provided the
			credentials have access. """
		self.client = PayPalHttpClient(self.environment)

	def object_to_json(self, json_data):
		"""
		Function to print all json data in an organized readable manner
		"""
		result = {}
		if sys.version_info[0] < 3:
			itr = json_data.__dict__.iteritems()
		else:
			itr = json_data.__dict__.items()
		for key,value in itr:
			# Skip internal attributes.
			if key.startswith("__"):
				continue
			result[key] = self.array_to_json_array(value) if isinstance(value, list) else\
						self.object_to_json(value) if not self.is_primittive(value) else\
						 value
		return result
	def array_to_json_array(self, json_array):
		result =[]
		if isinstance(json_array, list):
			for item in json_array:
				result.append(self.object_to_json(item) if  not self.is_primittive(item) \
								else self.array_to_json_array(item) if isinstance(item, list) else item)
		return result

	def is_primittive(self, data):
		return isinstance(data, str) or isinstance(data, unicode) or isinstance(data, int)


## Obtener los detalles de la transacción
class GetOrder(PayPalClient):

	#2. Set up your server to receive a call from the client
 
	def get_order(self, order_id):
		request = OrdersGetRequest(order_id)
	#3. Call PayPal to get the transaction
		response = self.client.execute(request)
		return response
	#4. Save the transaction in your database. Implement logic to save transaction to your database for future reference.
	# print 'Status Code: ', response.status_code
	# print 'Status: ', response.result.status
	# print 'Order ID: ', response.result.id
	# print 'Intent: ', response.result.intent
	# print 'Links:'
	# for link in response.result.links:
	#   print('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method))
	# print 'Gross Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code,
	#                    response.result.purchase_units[0].amount.value)

# """This driver function invokes the get_order function with
#    order ID to retrieve sample order details. """
# if __name__ == '__main__':
#   GetOrder().get_order('REPLACE-WITH-VALID-ORDER-ID')


class CaptureOrder(PayPalClient):

	#2. Set up your server to receive a call from the client
	def capture_order(self, order_id, debug=False):
		request = OrdersCaptureRequest(order_id)
	#3. Call PayPal to capture an order
		response = self.client.execute(request)
	#4. Save the capture ID to your database. Implement logic to save capture to your database for future reference.
		if debug:
			print ('Status Code: ', response.status_code)
			print ('Status: ', response.result.status)
			print ('Order ID: ', response.result.id)
			print ('Links: ')
		for link in response.result.links:
			print('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method))
		print ('Capture Ids: ')
		for purchase_unit in response.result.purchase_units:
			for capture in purchase_unit.payments.captures:
				print ('\t', capture.id)
		print ("Buyer:")
		# print "\tEmail Address: {}\n\tName: {}\n\tPhone Number: {}".format(response.result.payer.email_address,
		# response.result.payer.name.given_name + " " + response.result.payer.name.surname,
		# response.result.payer.phone.phone_number.national_number)
		return response