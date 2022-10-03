from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

#from .forms import UserForm
#from .models import User
from .forms import AccountForm
from .models import UserModel
from .models import Account
from .models import Index
from .models import IndexShort
from .models import Stock
from .models import Order
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyAuthBackend(object):
	def authenticate(self, email, password):    
		try:
			user = UserModel.objects.get(email=email)
			if user.check_password(password):
				return user
			else:
				return None
		except UserModel.DoesNotExist:
			logging.getLogger("error_logger").error("user with login %s does not exists " % login)
			return None
		except Exception as e:
			logging.getLogger("error_logger").error(repr(e))
			return None

	def get_user(self, user_id):
		try:
			user = UserModel.objects.get(sys_id=user_id)
			if user.is_active:
				return user
			return None
		except UserModel.DoesNotExist:
			logging.getLogger("error_logger").error("user with %(user_id)d not found")
			return None

def home(request):
	return render(request, 'home.html')

def manageAccount(request):
	user = request.user
	user_id = user.sys_id
	accounts = Account.objects.filter(user_id=user_id)
	context = {"accounts": accounts}
	return render(request, 'manageAccount.html', context)


def newInvestment(request):
	selected_index = None
	user = request.user
	user_id = user.sys_id
	query = Account.objects.filter(user_id='1')
	queryBool = query.exists()
	account=None
	key_id=None
	secret_key=None

	if query:
		account =  Account.objects.filter(user_id=user_id)[0]
		key_id= account.key_id
		secret_key= account.secret_key

	#FMP_key = '636e189c48f451ec431172e3ed273dc2'

	directorio = "C:/Users/Josema/Desktop/TFG/Datos/"

	results = IndexShort.objects.all()

	if request.method == "POST":
		if 'alpacaCredentials' in request.POST and 'loadIndexes' in request.POST:
			form = AccountForm(request.POST)
			if form.is_valid():
				api = tradeapi.REST(request.POST.get('key_id'), request.POST.get('secret_key'), "https://paper-api.alpaca.markets", api_version='v2')
				print(api.get_asset('AAPL'))

				account = form.save(commit=False)
				account.user = request.user
				account.balance=100000
				account.totalEquity=10000
				account.save()
				return redirect('/showAccount', pk=account.pk)
				context = {"form": form, "results": results, "queryBool": queryBool}
				return render(request, 'newInvestment.html', context)
		
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
					logger.exception('Error with: '+ ticker1 + str(e))
				
			total_market_cap = sum(market_caps)

			I = Index.objects.create(symbol=selected_index, marketCap=total_market_cap, account=account)


			tabla['Symbol'] = symbols
			tabla['MarketCap'] = market_caps
			tabla['Price'] = prices

			for item in market_caps:
				actual_weights.append(item/total_market_cap*100)
	
			tabla['Weight'] = actual_weights

			for i in tabla.index:
				cl=(tabla['Weight'][i]/100*I.equity)/tabla['Price'][i]

				alpaca = tradeapi.REST(account.key_id,
									account.secret_key,
									'https://paper-api.alpaca.markets')

				apiV2 = tradeapi.REST(account.key_id, account.secret_key, 'https://paper-api.alpaca.markets', api_version='v2')

				asset = apiV2.get_asset(tabla['Symbol'][i])
				if asset.fractionable:
					alpaca.submit_order(
					symbol=tabla['Symbol'][i],
					qty=cl,
					side="buy",
					type="market",
					time_in_force='day')
					O = Order.objects.create(stock=Stock.objects.create(symbol=tabla['Symbol'][i], price=tabla['Price'][i], marketCap=tabla['MarketCap'][i], actualWeight=tabla['Weight'][i], index=I), quantity=cl)

				if not asset.fractionable:
					alpaca.submit_order(
					symbol=tabla['Symbol'][i],
					qty=math.floor(cl),
					side="buy",
					type="market",
					time_in_force='day')
					O = Order.objects.create(stock=Stock.objects.create(symbol=tabla['Symbol'][i], price=tabla['Price'][i], marketCap=tabla['MarketCap'][i], actualWeight=tabla['Weight'][i], index=I), quantity=cl)

				#S = Stock.objects.create(symbol=tabla['Symbol'][i], price=tabla['Price'][i], marketCap=tabla['MarketCap'][i], actualWeight=tabla['Weight'][i], index=I)


			form = AccountForm()
			context = {"form": form, "results": results, "queryBool": queryBool}
			return render(request, 'manageAccount.html', context)
			#return HttpResponseRedirect('manageAccount.html')

	else:
		form = AccountForm()
		context = {"form": form, "results": results, "queryBool": queryBool}
		return render(request, 'newInvestment.html', context)




def showAccount(request):
	return render(request, 'showAccount.html')


def url1(symbol: str, api_key):
	return "https://financialmodelingprep.com/api/v3/market-capitalization/" + symbol + "?apikey=" + api_key

def url2(symbol: str, api_key):
	return "https://financialmodelingprep.com/api/v3/historical-price-full/" + symbol + "?apikey=" + api_key


def loadIndexesData(request):
	directorio = "C:/Users/Josema/Desktop/TFG/Datos"
	list=[]
	user = request.user
	user_id = user.sys_id
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


def loadIndexes(request):
	if request.method=='POST':     
		d = loadIndexesData(request)
		return redirect("/newInvestment")
		return render(request, 'newInvestment.html')
	else:
		return redirect("/newInvestment")


def listIndexes(request):
	results = IndexShort.objects.all()
	if not request.user.is_authenticated:
		return redirect('/account/login/')
	return render(request, 'manageAccount.html',{'results':results})