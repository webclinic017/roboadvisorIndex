from django.contrib import admin
from roboadvisor.models import UserModel, Account , Index, Stock

admin.site.register(UserModel)
admin.site.register(Account)
admin.site.register(Index)
admin.site.register(Stock)
