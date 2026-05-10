from django.db import models
from django.utils import timezone



class Stock(models.Model):
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    specification = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=100, blank=True, null=True)

    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item_name



class Sale(models.Model):
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    customer_name = models.CharField(max_length=100, blank=True, null=True)
    customer_contact = models.CharField(max_length=14, blank=True, null=True)
    item_type = models.CharField(max_length=100, blank=True, null=True)
    item_brand = models.CharField(max_length=100, blank=True, null=True)

    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item_name


class Deposit(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    method = models.CharField(max_length=100)
    item_name = models.CharField(max_length=100)
    nin = models.CharField(max_length=100, default="N/A")

    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Receipt(models.Model):
    number = models.IntegerField(default=0)
    customer_name = models.CharField(max_length=100)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.number)



class Supplier(models.Model):
    supplier_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    contact = models.CharField(max_length=14)
    email = models.EmailField()
    location = models.CharField(max_length=100)

    date = models.DateField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.supplier_name