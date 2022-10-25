from django.contrib import admin
from roboadvisor.models import Client, Account , Index, Stock

admin.site.register(Client)
admin.site.register(Account)
admin.site.register(Index)
admin.site.register(Stock)
