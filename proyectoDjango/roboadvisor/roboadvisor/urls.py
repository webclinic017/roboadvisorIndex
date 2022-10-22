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
from .views import listIndexes
from .views import loadIndexes
from .views import checkout
from .views import payment
from .views import pricing
from .views import rebalanceAll

urlpatterns = [
	path('__debug__/', include('debug_toolbar.urls')),
	path('', RedirectView.as_view(url=reverse_lazy('admin:index'))),
	path('admin/', admin.site.urls),
	path('home/', views.home,),
	#path('newUser/', newUser),
	path('manageAccount/', manageAccount),
	path('newInvestment_setAccount/', newInvestment_setAccount, name='newInvestment_setAccount'),
	#path('newInvestment_setIndex/', newInvestment_setIndex),
	path('newInvestment_setIndex/<int:pk>/',newInvestment_setIndex, name='newInvestment_setIndex'),
	path('showAccount/<int:pk>', showAccount, name='showAccount'),
	path('loadIndexes/<int:pk>', loadIndexes, name='loadIndexes'),
	path('checkout/', checkout),
	path('payment/', payment),
	path('pricing/', pricing),
	path('rebalanceAll/<int:pk>', rebalanceAll, name='rebalanceAll'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns