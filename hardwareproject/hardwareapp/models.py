from django.db import models


#create your models here
# STOCK MODEL
class Stock(models.Model):
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit_cost = models.FloatField()
    unit_price = models.FloatField()
    date = models.DateField(auto_now_add=True)
    supplier = models.CharField(max_length=100)
    specification = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)

    def __str__(self):
        return self.item_name
# SALE MODEL (SEPARATE)
class Sale(models.Model): # used to create a database table for sales in django
    product_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit_price = models.IntegerField()
    total = models.IntegerField(default=0)
    date = models.DateField()
    customer_name = models.CharField(max_length=100)
    customer_contact = models.CharField(max_length=100)
    item_type = models.CharField(max_length=100)
    item_brand = models.CharField(max_length=100)

    total = models.IntegerField(default=0)  

    def __str__(self):
        return self.product_name
    
class Deposit(models.Model):
    amount = models.FloatField()
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    method = models.CharField(max_length=100)
    purpose = models.CharField(max_length=100)
    balance = models.FloatField(default=0)
    
def __str__(self):
       return self.name

class Receipt(models.Model):
    number = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    customer_name = models.CharField(max_length=100)
    subtotal = models.FloatField(default=0)
    tax = models.FloatField(default=0)
    total = models.FloatField(default=0)
    paid = models.FloatField(default=0)
    balance = models.FloatField(default=0)  

    def __str__(self): # this is the receipt number that is displayed on the receipt page
        return self.number


  