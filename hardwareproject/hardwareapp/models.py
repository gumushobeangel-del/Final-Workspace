from django.db import models



# STOCK

class Stock(models.Model):
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    specification = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)

    date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item_name



# SALE

class Sale(models.Model):
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    customer_name = models.CharField(max_length=100)
    customer_contact = models.CharField(max_length=14)
    item_type = models.CharField(max_length=100)
    item_brand = models.CharField(max_length=100)

    date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item_name


# DEPOSIT

class Deposit(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    method = models.CharField(max_length=100)
    item_name = models.CharField(max_length=100)
    nin = models.CharField(max_length=100, default="N/A")

    date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



# RECEIPT

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


# SUPPLIER

class Supplier(models.Model):
    supplier_name = models.CharField(max_length=100)#prevents user from entering more than 100 characters
    company = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    email = models.EmailField()
    location = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.supplier_name



class Supplier(models.Model):
    supplier_name = models.CharField(max_length=100)
    date = models.DateField(null=True, blank=True)
    company = models.CharField(max_length=100)
    contact = models.CharField(max_length=14)#prevents user from entering more than 14 characters
    email = models.EmailField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.supplier_name

