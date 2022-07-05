from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from .forms import UserForm
from .models import User

def home(request):
	return render(request, 'home.html')


def newUser(request):
	if request.method == "POST":
		form = UserForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect("/manageAccounts")  
	else:
		form = UserForm()
	return render(request, "newUser.html", {"form": form })

def manageAccounts(request):
	return render(request, 'manageAccounts.html')
