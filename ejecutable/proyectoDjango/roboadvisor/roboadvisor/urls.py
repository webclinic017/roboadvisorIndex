from django.urls import path, include, reverse_lazy
from . import views

from django.views.generic.base import RedirectView

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
#from rbdx.views import newUser
from .views import manageAccount
from .views import newInvestment_setAccount
from .views import newInvestment_setIndex
from .views import showAccount
from .views import loadIndexes
from .views import checkout
from .views import payment
from .views import pricing
from .views import rebalance
from .views import signupView
from .views import loginView
from .views import logoutView
from .views import home
from .views import uploadFile
from .views import deleteAccount

urlpatterns = [
	path('', views.home),
	path('admin/', admin.site.urls),
	#path('base/', views.base),
	path('home/', views.home),
	path('signup/', signupView, name='signup'),
	path('login/', loginView, name='login'),
	path('logout/', logoutView, name='logout'),
	path('showAccount/<int:pk>', showAccount, name='showAccount'),
	#path('newUser/', newUser),
	path('manageAccount/', manageAccount),
	path('newInvestment_setAccount/', newInvestment_setAccount, name='newInvestment_setAccount'),
	#path('newInvestment_setIndex/', newInvestment_setIndex),
	path('newInvestment_setIndex/<int:pk>/',newInvestment_setIndex, name='newInvestment_setIndex'),
	path('showAccount/<int:pk>', showAccount, name='showAccount'),
	path('loadIndexes/<int:pk>', loadIndexes, name='loadIndexes'),
	path('deleteAccount/<int:pk>', deleteAccount, name='deleteAccount'),
	path('checkout/', checkout),
	path('payment/', payment),
	path('pricing/', pricing),
	path('rebalance/<int:pk>', rebalance, name='rebalance'),
	path('uploadFile/<int:pk>', uploadFile, name='uploadFile'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)