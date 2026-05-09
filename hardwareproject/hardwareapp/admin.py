from django.contrib import admin
from .models import Stock, Sale,Deposit, Supplier, Receipt

# Register your models here.
admin.site.register(Stock)
admin.site.register(Sale)
admin.site.register(Deposit)
admin.site.register(Supplier)
admin.site.register(Receipt)

