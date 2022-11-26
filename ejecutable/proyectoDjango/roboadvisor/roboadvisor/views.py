from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.conf import settings
from .forms import AccountForm
from .forms import UploadFileForm
from .models import Client
from .models import Account
from .models import Index
from .models import IndexShort
from .models import Stock
from .models import Order
from .models import Purchase
from .models import UploadFile
import logging
import os
import pandas as pd
import requests
from alpaca_trade_api.rest import REST, TimeFrame
import alpaca_trade_api as tradeapi
import math
import yfinance as yf
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
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import math 
from statistics import mean
from django.contrib.auth.decorators import login_required

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
	check = user.is_authenticated
	context = {"user": user, "check": check}
	return render(request, 'home.html', context)

@login_required(login_url='/login')
def manageAccount(request):
	user = request.user
	user_id = user.id

	accounts = Account.objects.filter(user_id=user_id)
	portfolioValues = []
	balanceChanges = []

	for a in accounts:
		try:
			api = tradeapi.REST(
			key_id=a.key_id,
			secret_key=a.secret_key,
			base_url='https://paper-api.alpaca.markets',
			api_version='v2')
			alpacaAccount = api.get_account()
			portfolioValues.append(alpacaAccount.portfolio_value)
			balanceChanges.append(float("{:.2f}".format((float(alpacaAccount.equity) - float(alpacaAccount.last_equity))/100)))
		except:
			portfolioValues.append("UNLINKED")
			balanceChanges.append(0)


	accPortBalance = zip(accounts, portfolioValues, balanceChanges)
	
	context = {"accPortBalance": accPortBalance}
	return render(request, 'manageAccount.html', context)

@login_required(login_url='/login')
def newInvestment_setAccount(request):
	results = IndexShort.objects.all()
	try:
		user = request.user
		account=None
		if request.method == "POST":
			if 'alpacaCredentials' in request.POST:
				form = AccountForm(request.POST)
				if form.is_valid():
					try:
						api = tradeapi.REST(request.POST.get('key_id'), request.POST.get('secret_key'), "https://paper-api.alpaca.markets", 
							api_version='v2')
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
						form = AccountForm()
						messages.add_message(request, messages.ERROR, "Credentials wrong. Please use the credentials of a new Alpaca account.")
						context = {"form": form, "results": results}
						return render(request, 'newInvestment_setAccount.html', context)
		else:
			form = AccountForm()
			context = {"form": form, "results": results}
			return render(request, 'newInvestment_setAccount.html', context)

	except Exception as e:
		form = AccountForm()
		messages.add_message(request, messages.ERROR, "Fail to load. Please try again.")
		context = {"form": form, "results": results}
		return render(request, 'newInvestment_setAccount.html', context)
		
	form = AccountForm()
	context = {"form": form, "results": results}
	return render(request, 'newInvestment_setAccount.html', context)	
		
@login_required(login_url='/login')
def newInvestment_setIndex(request, pk):

	selected_index = None
	user = request.user
	user_id = user.id

	account= get_object_or_404(Account, pk=pk)

	results = IndexShort.objects.all()

	directorio = settings.MEDIA_ROOT

	finnhub_client = finnhub.Client(api_key="cci63qiad3ibcn4bhk6g")

	comissionPerBuy=0.02

	contadorT=0
	contadorY=0

	iteraciones=115
	cont=0

	ind = Index.objects.filter(account_id= account.id)
	booInd = ind.exists()

	if request.method == "POST":
		if 'newInvestment_setIndex' in request.POST:
			try:
				selected_index = request.POST.get("index")
				df =pd.read_csv(directorio+"/"+selected_index+'.csv')
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
							messages.add_message(request, messages.ERROR, "Error with: "+ symbol + ": " + str(e))
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
								messages.add_message(request, messages.ERROR, "Error with: "+ symbol + ": " + str(e))
				
				total_market_cap = sum(market_caps)

				I = Index.objects.create(symbol=selected_index, marketCap=total_market_cap, account=account)

				for s in symbols:
					s.replace('-', '.', 1)

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

					try:
						asset = apiV2.get_asset(tabla['Symbol'][i])

						if asset.fractionable and cl>0:
							alpaca.submit_order(
							symbol=tabla['Symbol'][i],
							qty=cl,
							side="buy",
							type="market",
							time_in_force='day')
							cont=cont+(cl*tabla['Price'][i])
							O = Order.objects.create(stock=Stock.objects.create(symbol=tabla['Symbol'][i], lastPrice=tabla['Price'][i], 
								marketCap=tabla['MarketCap'][i], actualWeight=tabla['Weight'][i], index=I), quantity=cl, price=tabla['Price'][i])

						if not asset.fractionable and math.floor(cl)>0:
							alpaca.submit_order(
							symbol=tabla['Symbol'][i],
							qty=math.floor(cl),
							side="buy",
							type="market",
							time_in_force='day')
							cont=cont+(cl*tabla['Price'][i])
							O = Order.objects.create(stock=Stock.objects.create(symbol=tabla['Symbol'][i], lastPrice=tabla['Price'][i], 
								marketCap=tabla['MarketCap'][i], actualWeight=tabla['Weight'][i], index=I), quantity=cl, price=tabla['Price'][i])
					except:
						pass

				
				return HttpResponseRedirect("/manageAccount/")
			except Exception as e:
				messages.add_message(request, messages.ERROR, "Error with: " + str(e))
				form = AccountForm()
				context = {"form": form, "results": results, "account":account}
				
				return redirect("/newInvestment_setIndex/"+str(pk))
				return render(request, 'newInvestment_setIndex.html', context)

	else:
		form = AccountForm()
		context = {"form": form, "results": results, "account":account, "booInd": booInd}
		return render(request, 'newInvestment_setIndex.html', context)


@login_required(login_url='/login')
def showAccount(request, pk):
	user = request.user
	user_id = user.id
	account=Account.objects.get(id=pk)
	api = tradeapi.REST(account.key_id, account.secret_key, 'https://paper-api.alpaca.markets', api_version='v2')

	ind = Index.objects.get(account_id=pk)
	stocks = Stock.objects.filter(index_id=ind.id)
	orders = []
	orders1 = []
	symbols = []
	dates = []
	for s in stocks:
		orders.append(Order.objects.filter(stock_id=s.id))
		symbols.append(s.symbol)

	for o in orders:
		for i in range(0,len(o)):
			orders1.append(o[i])
	
	for o1 in orders1:
		dates.append(o1.date)


	df = pd.DataFrame(dates, columns =['Date'])
	df['Date'] = pd.to_datetime(df['Date'])
	recentDate = datetime.strptime(df['Date'].max().strftime("%Y-%m-%d"), "%Y-%m-%d")
	today = datetime.strptime((datetime.now()).strftime("%Y-%m-%d"), "%Y-%m-%d")
	diff = str(today - recentDate).split(' ')
	rebalanceBool=True
	try:
		#rebalanceBool = int(diff[0]) > 7
		rebalanceBool=True
	except:
		pass


	numberStocks = stocks.count()


	chart7D(stocks, api)

	pieChart(stocks)

	context = {"orders": orders1, "index":ind, "account":account, "numberStocks":numberStocks, "recentDate": recentDate, "rebalanceBool": rebalanceBool}
	return render(request, 'showAccount.html' , context)

@login_required(login_url='/login')
def loadIndexesData(request):
	directorio = settings.MEDIA_ROOT
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
			if i not in list2:
				I = IndexShort.objects.create(symbol=i)

@login_required(login_url='/login')
def loadIndexes(request, pk):

	if request.method=='POST':     
		d = loadIndexesData(request)
		return redirect("/newInvestment_setIndex/"+str(pk))
		return render(request, 'newInvestment_setIndex.html')
	else:
		return redirect("/newInvestment_setIndex/"+str(pk))

@login_required(login_url='/login')
def rebalance(request, pk):
	user = request.user
	user_id = user.id
	account=Account.objects.get(id=pk)


	finnhub_client = finnhub.Client(api_key="cci63qiad3ibcn4bhk6g")

	comissionPerBuy=0.02

	contadorT=0
	contadorY=0

	iteraciones=115
	cont=0

	if request.method == "POST":
		if 'rebalance' in request.POST:
			try:
				tabla = pd.DataFrame(columns = ['Symbol', 'Market Cap', 'Actual Prices', 'Old Weight' 'Actual Weight', 'Difference'])
				sellTable = pd.DataFrame(columns = ['Symbol', 'Market Cap', 'Actual Prices', 'Old Weight' 'Actual Weight', 'Difference'])
				buyTable = pd.DataFrame(columns = ['Symbol', 'Market Cap', 'Actual Prices', 'Old Weight' 'Actual Weight', 'Difference'])

				apiV2 = tradeapi.REST(account.key_id, account.secret_key, 'https://paper-api.alpaca.markets', api_version='v2')
				alpaca = tradeapi.REST(account.key_id, account.secret_key, 'https://paper-api.alpaca.markets')

				
				alpacaAccount = apiV2.get_account()

				account.balance = alpacaAccount.equity
				account.save()

				symbols = []
				marketCaps = []
				actualPrices = []
				oldWeights = []
				actualWeights = []
				difference = []

				total_market_cap = 0

				indexSelected = Index.objects.get(account_id=account.id)
				stocks = Stock.objects.filter(index_id=indexSelected.id)

				orders = apiV2.list_orders(status='filled',
				#limit=100,
				#nested=True  # show nested multi-leg orders
				)


				if orders: 
					if user.client.is_premium is False:
						for item in stocks:
							try:

								oldWeights.append(item.actualWeight)
								symbol=item.symbol.replace('.', '-', 1)

								ticker_yahoo = yf.Ticker(symbol)
								data = ticker_yahoo.history()
								price = data['Close'].iloc[-1]
								marketCap=web.get_quote_yahoo(symbol)['marketCap'][0]
									

								marketCaps.append(marketCap)
								symbols.append(symbol)
								actualPrices.append(price)

								item.price=price
								item.marketCap=marketCap
								item.save()

								total_market_cap=total_market_cap+marketCap


							except Exception as e:
								messages.add_message(request, messages.ERROR, "Error with: "+ symbol + str(e))
					else:
						for item in stocks:
							if contadorY>=iteraciones and contadorT<60:
								time.sleep(61-contadorT)
								contadorT=0
								contadorY=0
			
							if contadorY<iteraciones:
								try: 
									oldWeights.append(item.actualWeight)
									symbol=item.symbol.replace('.', '-', 1)
											
									instanteInicial = time.time()
											
									last_quote = finnhub_client.quote(symbol)['c']
									marketCap=finnhub_client.company_profile2(symbol=symbol)['marketCapitalization']
											
									instanteFinal = time.time()
									tiempo = instanteFinal - instanteInicial
											
									contadorY=contadorY+2
											
									contadorT=contadorT+tiempo

									marketCaps.append(marketCap)
									symbols.append(symbol)
									actualPrices.append(last_quote)

									item.price=last_quote
									item.marketCap=marketCap
									item.save()

									total_market_cap=total_market_cap+marketCap
											
								except Exception as e:
									#time.sleep(35)
									messages.add_message(request, messages.ERROR, "Error with: "+ symbol + str(e))
						
						
					indexSelected.marketCap=total_market_cap
					indexSelected.save()

					tabla['Symbol'] = symbols
					tabla['Market Cap'] = marketCaps
					tabla['Actual Prices'] = actualPrices
					tabla['Old Weight'] = oldWeights


					for item in marketCaps:
						actualWeights.append(item/total_market_cap*100)
				
					tabla['Actual Weight'] = actualWeights


					for item in tabla.index:
						difference.append(tabla['Actual Weight'][item]-tabla['Old Weight'][item])
						s = Stock.objects.get(symbol=tabla['Symbol'][item], index_id=indexSelected.id)
						print(s)
						s.marketCap=tabla['Market Cap'][item]
						s.save()

					tabla['Difference'] = difference

					listSells=[]

					print(tabla)
					print("-------------------------------------------------------")
					print("-------------------------------------------------------")

					for item in tabla.index:
						if tabla['Difference'][item]<0:
							listSells.append(tabla['Symbol'][item])

					for item in listSells:
						i=tabla.loc[tabla['Symbol'] == item]
						sellTable = pd.concat([sellTable, pd.DataFrame.from_records(i)], ignore_index=True)

					print(sellTable)
					print("-------------------------------------------------------")

					#ventas = tabla[tabla['Difference'].startswith("-")]
					#print(ventas)
					buyTable = (tabla.set_index('Symbol').subtract(sellTable.set_index('Symbol'), fill_value=0)).reset_index()
					buyTable = buyTable.drop(buyTable[buyTable['Market Cap'] == 0.0].index).set_index('Symbol').reset_index()
					print(buyTable)
					print("-------------------------------------------------------")
					print("-------------------------------------------------------")


					#VENTAS

					for i in sellTable.index:
						cl=(abs(sellTable['Difference'][i])*float(account.balance)/100/(sellTable['Actual Prices'][i]+sellTable['Actual Prices'][i]*comissionPerBuy))

						try:
							asset = apiV2.get_asset(sellTable['Symbol'][i])
							if asset.fractionable and cl>0:
								alpaca.submit_order(
								symbol=sellTable['Symbol'][i],
								qty=cl,
								side="sell",
								type="market",
								time_in_force='day')
								print(sellTable['Symbol'][i], "Quantity: ", cl, "Sell done")
								#cont=cont+(cl*sellTable['Price'][i])

								O = Order.objects.create(stock=Stock.objects.get(symbol=sellTable['Symbol'][i], index_id=indexSelected.id), 
									quantity=-cl, price=sellTable['Actual Prices'][i])
								s1 = Stock.objects.get(symbol=sellTable['Symbol'][i], index_id=indexSelected.id)
								s1.actualWeight=sellTable['Actual Weight'][i]
								print(s1, s1.actualWeight)
								s1.save()
				
							if not asset.fractionable and math.floor(cl)>0:
								alpaca.submit_order(
								symbol=sellTable['Symbol'][i],
								qty=math.floor(cl),
								side="sell",
								type="market",
								time_in_force='day')
								print(sellTable['Symbol'][i], "Quantity: ", cl, "Sell done")
								#cont=cont+(cl*sellTable['Price'][i])

								O = Order.objects.create(stock=Stock.objects.get(symbol=sellTable['Symbol'][i], index_id=indexSelected.id), 
									quantity=-cl, price=sellTable['Actual Prices'][i])
								s1 = Stock.objects.get(symbol=sellTable['Symbol'][i], index_id=indexSelected.id)
								s1.actualWeight=sellTable['Actual Weight'][i]
								print(s1, s1.actualWeight)
								s1.save()
						except:
							pass

					for i in buyTable.index:
						cl=(buyTable['Difference'][i]*float(account.balance)/100/(buyTable['Actual Prices'][i]+buyTable['Actual Prices'][i]*comissionPerBuy))
						try:
							asset = apiV2.get_asset(buyTable['Symbol'][i])
							if asset.fractionable and cl>0:
								alpaca.submit_order(
								symbol=buyTable['Symbol'][i],
								qty=cl,
								side="buy",
								type="market",
								time_in_force='day')
								print(buyTable['Symbol'][i],"Quantity: ", cl, "Buy done")
								#cont=cont+(cl*buyTable['Price'][i])
								O = Order.objects.create(stock=Stock.objects.get(symbol=buyTable['Symbol'][i], index_id=indexSelected.id), 
									quantity=cl, price=buyTable['Actual Prices'][i])
								s1 = Stock.objects.get(symbol=buyTable['Symbol'][i], index_id=indexSelected.id)
								s1.actualWeight=buyTable['Actual Weight'][i]
								s1.save()

							if not asset.fractionable and math.floor(cl)>0:
								alpaca.submit_order(
								symbol=buyTable['Symbol'][i],
								qty=math.floor(cl),
								side="buy",
								type="market",
								time_in_force='day')
								print(buyTable['Symbol'][i],"Quantity: ", cl, "Buy done")
								#cont=cont+(cl*buyTable['Price'][i])
								O = Order.objects.create(stock=Stock.objects.get(symbol=buyTable['Symbol'][i], index_id=indexSelected.id), 
									quantity=cl, price=buyTable['Actual Prices'][i])
								s1 = Stock.objects.get(symbol=buyTable['Symbol'][i], index_id=indexSelected.id)
								s1.actualWeight=buyTable['Actual Weight'][i]
								s1.save()
						except:
							pass



					return redirect("/manageAccount/")
					return render(request, 'manageAccount.html', context)

			except Exception as e:
				#logger.exception('Error with: '+ str(e))
				messages.add_message(request, messages.ERROR, "Error rebalancing:" + str(e))
				accounts = Account.objects.filter(user_id=user_id)
				context = {"accounts": accounts}
				
				return redirect("/manageAccount/")
				return render(request, 'manageAccount.html', context)
		

	return redirect("/manageAccount/")
	return render(request, 'manageAccount.html', context)




@login_required(login_url='/login')
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


def pricing(request):
	user = request.user
	context = {"user": user}
	return render(request, 'pricing.html', context)

@login_required(login_url='/login')
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


@login_required(login_url='/login')
def uploadFile(request, pk):
	if request.method == 'POST':
		file2 = request.FILES['file']
		document = UploadFile.objects.create(file=file2)
		document.save()
		return redirect("/newInvestment_setIndex/"+str(pk))
		return render(request, 'newInvestment_setIndex.html')
	else:
		return redirect("/newInvestment_setIndex/"+str(pk))

@login_required(login_url='/login')
def deleteAccount(request, pk):
	if request.method == 'POST':
		account = Account.objects.get(id=pk).delete()
		return redirect("/manageAccount")
		return render(request, 'manageAccount.html')
	else:
		return redirect("/manageAccount")


def chart7D(stocks, api):
	try:
		reg = []

		df = pd.DataFrame(columns = ['Symbol', 'Seven', 'Six', 'Five', 'Four', 'Three', 'Two', 'One'])
		df.set_index('Symbol')

		today = datetime.now().strftime('%Y-%m-%d')
		yesterday = (datetime.now()- timedelta(days=1)).strftime('%Y-%m-%d')
		sevenDaysAgo = (datetime.now()- timedelta(days=12)).strftime('%Y-%m-%d')

		for s in stocks:
			reg = []

			for i in range(0,7):
				try:
					reg.append((yf.download(s.symbol, start=sevenDaysAgo, end=yesterday, progress=False)['Close'][i])*s.actualWeight)
				except:
					pass	

			new_row = {'Symbol':[s.symbol], 'Seven':[reg[0]], 'Six':[reg[1]], 'Five':[reg[2]], 'Four':[reg[3]], 'Three':[reg[4]], 'Two':[reg[5]], 'One':[reg[6]]}
			df=pd.concat([df, pd.DataFrame.from_records(new_row)], ignore_index=True)

		fig, ax = plt.subplots()
		dias = ['-7 days', '-6 days', '-5 days', '-4 days', '-3 days', '-2 days', '-1 day']
		regs = {'Index':[mean(df['Seven']), mean(df['Six']), mean(df['Five']), mean(df['Four']), 
										 mean(df['Three']), mean(df['Two']), mean(df['One'])]}
		ax.set_ylabel("Average weekly price change of the index")
		ax.plot(dias, regs['Index'], linestyle = 'solid', color = 'b')
		ax.fill_between(dias, regs['Index'], interpolate=True, color='c')

		reg1 = mean(df['Seven']), mean(df['Six']), mean(df['Five']), mean(df['Four']), mean(df['Three']), mean(df['Two']), mean(df['One'])



		ax.set_ylim(math.floor(min(reg1)),math.ceil(max(reg1)))
		ax.set_yticks(range(math.floor(min(reg1)),math.ceil(max(reg1)+1)))

		plt.savefig('static/plot.png')
	except:
		return redirect("/manageAccount")

def pieChart(stocks):
	fig, ax = plt.subplots()
	symbols = []
	weights = []
	for s in stocks:
		symbols.append(s.symbol)
		weights.append(s.actualWeight)

	df = pd.DataFrame(data = {'Symbols': symbols, 'Weights': weights}).sort_values('Weights', ascending = False)

	df2 = df[:9].copy()

	new_row = pd.DataFrame(data = {
	'Symbols' : ['Others'],
	'Weights' : [df['Weights'][9:].sum()]})

	df2 = pd.concat([df2, new_row])

	plt.pie(df2['Weights'], labels = df2['Symbols'])
	plt.title("Total composition adjusted to weights", bbox={'facecolor':'0.8', 'pad':5})
	plt.savefig('static/pie.png')


	
