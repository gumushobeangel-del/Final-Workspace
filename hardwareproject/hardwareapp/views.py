from django.shortcuts import render, redirect
from .models import Stock, Sale, Deposit


# HOME PAGE VIEW
def index(request):
    return render(request, 'index.html')


# LOGIN PAGE VIEW

def log(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # VALIDATION (correct indentation)
        if email == "admin@gmail.com" and password == "1234":
            return redirect("stock")#go to the stock page
        

        else:
            return render(request, "log.html", {
                "error": "Invalid email or password"
            })
        return redirect("dash")
    return render(request, "log.html")  # shows the log page properly




# SALES PAGE VIEW


def sales(request):
    if request.method == "POST":#saves the data in the database
        product_name = request.POST.get('product_name')
        quantity = request.POST.get('quantity')
        unit_price = request.POST.get('unit_price')
        customer_name = request.POST.get('customer_name')
        customer_contact = request.POST.get('customer_contact')
        item_type = request.POST.get('item_type')
        item_brand = request.POST.get('item_brand')
        date = request.POST.get('date')

        # VALIDATION (correct indentation)
        if not quantity or not unit_price:
            return render(request, 'sales.html', {
                'error': 'Quantity and Unit Price are required'
            })

        quantity = int(quantity)
        unit_price = int(unit_price)

        total = quantity * unit_price# this makes the system calculate the total automatically

        Sale.objects.create(
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
            customer_name=customer_name,
            customer_contact=customer_contact,
            item_type=item_type,
            item_brand=item_brand,
            date=date,
            total=total
        )

        return redirect('sales')
    print("SAVED SUCCESSFULLY")

    sales = Sale.objects.all()#shows live data on the web page
    return render(request, 'sales.html', {'sales': sales})

# STOCK MANAGEMENT VIEW
def stock_view(request):
    if request.method == "POST":

        quantity = request.POST.get("quantity")

        if not quantity:
            return render(request, "stock.html", {
                "stocks": Stock.objects.all(),
                "error": "Quantity is required"
            })

        Stock.objects.create(
            item_name=request.POST.get("item_name"),
            quantity=int(quantity),
            unit_cost=float(request.POST.get("unit_cost")),
            unit_price=float(request.POST.get("unit_price")),
            date=request.POST.get("date"),
            supplier=request.POST.get("supplier"),
            specification=request.POST.get("specification"),
            payment_method=request.POST.get("payment_method"),
        )

        return redirect("stock")

    stocks = Stock.objects.all()#shows live data on the web page
    return render(request, "stock.html", {"stocks": stocks})





# DASHBOARD
def dash(request):
    return render(request, 'dash.html')


# DEPOSIT PAGE
from decimal import Decimal

def deposit(request):
    if request.method == 'POST':
        amount = float(request.POST.get('amount')) # this is the amount the user wants to deposit
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        method = request.POST.get('method')
        purpose = request.POST.get('purpose')

        # get the last deposit and add the amount to it
        last_deposit = Deposit.objects.order_by('-id').first()

        if last_deposit:
            balance = last_deposit.balance + amount
        else:
            balance = amount

        Deposit.objects.create(
            amount=amount,
            name=name,
            phone=phone,
            method=method,
            purpose=purpose,
            balance=balance
        )

        print("SAVED SUCCESSFULLY") 
        return redirect('deposit')

    return render(request, 'deposit.html')

# SUPPLIERS PAGE
def suppliers(request):
    return render(request, 'suppliers.html')
      


# SIGNUP PAGE
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


#this saves the user data in the database
def sign(request):
    #this handles the sign up request
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        print("USERNAME:", username)
        print("EMAIL:", email)


        if not username or not password:
            print("MISSING DATA")
            return render(request, 'sign.html', {
                'error': 'Username and password required'
            })
        

        #if the user already exists then it will return an error
        if User.objects.filter(username=username).exists():
            print("USER EXISTS")
            return render(request, 'sign.html', {
                'error': 'User already exists'
            })

        # this creates the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
       #saves the user
        print("USER CREATED:", user)

        return redirect('sales')

    return render(request, 'sign.html')