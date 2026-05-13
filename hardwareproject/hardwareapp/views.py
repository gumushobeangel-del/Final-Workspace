from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login

from .models import Stock, Sale, Deposit, Receipt, Supplier,Register


# HOME


def index(request):
    return render(request, "index.html")

#sign
def sign(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")

        users = {
            "admin": {"username": "Angellina", "password": "angel266"},
            "sales": {"username": "kevin", "password": "kevin256"},
            "stock_manager": {"username": "alvin", "password": "alvie233"},
        }

        if role in users:
            if (
                username.lower().strip() == users[role]["username"].lower().strip()
                and password == users[role]["password"]
            ):
                request.session["role"] = role
                request.session["username"] = username

                redirect_map = {
                    "admin": "dash",
                    "sales": "sales",
                    "stock_manager": "stock",
                }

                return redirect(redirect_map[role])

        return render(request, "sign.html", {"error": "Wrong login details"})

    return render(request, "sign.html")


def register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')

        Register.objects.create(
            name=name,
            phone=phone,
            email=email,
            address=address
        )

        return redirect('register')

    customers = Register.objects.all().order_by('-id')

    return render(request, 'register.html', {'customers': customers})

def edit_customer(request, id):
    customer = get_object_or_404(Register, id=id)

    if request.method == "POST":
        customer.name = request.POST.get("name")
        customer.phone = request.POST.get("phone")
        customer.email = request.POST.get("email")
        customer.address = request.POST.get("address")

        customer.save()
        return redirect("register")

    return render(request, "edit_customer.html", {"customer": customer})

def delete_customer(request, id):
    customer = get_object_or_404(Register, id=id)
    customer.delete()
    return redirect("register")


#login
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # ONLY ADMIN ALLOWED
        if username == "Angellina" and password == "angel266":

            request.session["role"] = "admin"
            request.session["username"] = username

            return redirect("dash")

        return render(request, "log.html", {
            "error": "Only admin can log in here"
        })

    return render(request, "log.html")

# DASHBOARD
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from datetime import datetime, timedelta

from .models import Stock, Sale, Supplier


def dash(request):
    role = request.session.get("role")

    # BLOCK NON-ADMINS
    if role != "admin":
        return redirect("sign") 

    # TOTAL PRODUCTS
    total_products = Stock.objects.count()

    # LOW STOCK
    low_stock = Stock.objects.filter(quantity__lt=20).count()

    # SUPPLIERS
    suppliers = Supplier.objects.count()

    # TOTAL SALES
    total_sales = Sale.objects.aggregate(total=Sum('total'))['total'] or 0

    today = datetime.today().date()
    week = today - timedelta(days=7)
    month = today.replace(day=1)

    today_sales = Sale.objects.filter(date=today).aggregate(total=Sum('total'))['total'] or 0
    week_sales = Sale.objects.filter(date__gte=week).aggregate(total=Sum('total'))['total'] or 0
    month_sales = Sale.objects.filter(date__gte=month).aggregate(total=Sum('total'))['total'] or 0

    top_product = (
        Sale.objects.values('item_name')
        .annotate(total_qty=Sum('quantity'))
        .order_by('-total_qty')
        .first()
    )

    stocks = Stock.objects.all()

    context = {
        "total_products": total_products,
        "low_stock": low_stock,
        "suppliers": suppliers,
        "total_sales": total_sales,
        "today_sales": today_sales,
        "week_sales": week_sales,
        "month_sales": month_sales,
        "top_product": top_product,
        "stocks": stocks,
    }

    return render(request, "dash.html", context)



#stock
def stock_view(request):
    if request.method == "POST":
        item_name = request.POST.get("item_name")
        quantity = int(request.POST.get("quantity") or 0)
        unit_cost = float(request.POST.get("unit_cost") or 0)
        unit_price = float(request.POST.get("unit_price") or 0)

        # Prevent empty values
        if not item_name:
            return render(request, "stock.html", {
                "error": "Item name is required"
            })
        
        #prevents negatives
        if quantity <= 0 or unit_cost <= 0 or unit_price <= 0:
            return render(request, "stock.html", {
                "error": "All values must be greater than 0"
            })

        # ONLY runs on POST
        Stock.objects.create(
            item_name=item_name,
            quantity=quantity,
            unit_cost=unit_cost,
            unit_price=unit_price,
            date=request.POST.get("date"),
            specification=request.POST.get("specification"),
            payment_method=request.POST.get("payment_method"),
        )

    stocks = Stock.objects.all()
    return render(request, "stock.html", {"stocks": stocks})


# SALES
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Stock, Sale

def sales(request):

    if request.method == "POST":

        stock_id = request.POST.get("stock_id")
        quantity = int(request.POST.get("quantity") or 0)
        unit_price = float(request.POST.get("unit_price") or 0)

        # VALIDATION
        if quantity <= 0 or unit_price <= 0:
            return render(request, "sales.html", {
                "error": "Quantity and Unit Price must be greater than 0"
            })

        # GET STOCK (SAFE)
        stock = get_object_or_404(Stock, id=stock_id)

        # CHECK STOCK
        if stock.quantity < quantity:
            return render(request, "sales.html", {
                "error": "Not enough stock available!"
            })

        # REDUCE STOCK
        stock.quantity -= quantity
        stock.save()

        total = quantity * unit_price

        # SAVE SALE
        Sale.objects.create(
            item_name=stock.item_name,
            quantity=quantity,
            unit_price=unit_price,
            total=total,
            customer_name=request.POST.get("customer_name"),
            customer_contact=request.POST.get("customer_contact"),
            item_type=request.POST.get("item_type"),
            item_brand=request.POST.get("item_brand"),
            date=request.POST.get("date")
        )

        return redirect("sales")

    stocks = Stock.objects.all().order_by("-id")
    sales = Sale.objects.all().order_by("-id")

    return render(request, "sales.html", {
        "stocks": stocks,
        "sales": sales
    })


#Deposit
# Put this at the TOP of views.py (outside the function)
ITEM_PRICES = {
    "Cement": 30000,
    "Glass": 15000,
    "Iron Sheets": 20000,
    "Iron Bars": 27000,
}


def deposit(request):

    if request.method == "POST":

        amount = float(request.POST.get("amount") or 0)
        quantity = int(request.POST.get("quantity") or 0)
        item_name = request.POST.get("item_name")

        # Validation
        if amount <= 0:
            return render(request, "deposit.html", {
                "error": "Amount must be greater than 0"
            })

        if quantity <= 0:
            return render(request, "deposit.html", {
                "error": "Quantity must be greater than 0"
            })

        # Get price
        price = ITEM_PRICES.get(item_name, 0)

        if price == 0:
            return render(request, "deposit.html", {
                "error": "Invalid item selected"
            })

        # Calculations
        total_cost = price * quantity
        balance = amount - total_cost

        # Save
        Deposit.objects.create(
            amount=amount,
            quantity=quantity,
            balance=balance,
            name=request.POST.get("name"),
            phone=request.POST.get("phone"),
            method=request.POST.get("method"),
            item_name=item_name,
            nin=request.POST.get("nin") or "N/A",
            date=request.POST.get("date")
        )

        return redirect("deposit")

    # GET request (no calculations here)
    deposits = Deposit.objects.all()

    return render(request, "deposit.html", {
        "deposits": deposits
    })
# RECEIPT

def receipt(request, id):
    sale = get_object_or_404(Sale, id=id)
    return render(request, "receipt.html", {"sale": sale})


# SUPPLIERS


def suppliers(request):

    if request.method == "POST":

        Supplier.objects.create(
            supplier_name=request.POST.get("supplier_name"),
            date=request.POST.get("date"),
            company=request.POST.get("company"),
            contact=request.POST.get("contact"),
            email=request.POST.get("email"),
            location=request.POST.get("location"),
        )

        return redirect("supplier")  

    suppliers = Supplier.objects.all()

    return render(request, "suppliers.html", {
        "suppliers": suppliers
    })



# EDIT STOCK
def edit_stock(request, id):
    stock = get_object_or_404(Stock, id=id)

    if request.method == "POST":

        stock.item_name = request.POST.get("item_name")
        stock.quantity = request.POST.get("quantity")
        stock.unit_cost = request.POST.get("unit_cost")
        stock.unit_price = request.POST.get("unit_price")
        stock.specification = request.POST.get("specification")
        stock.payment_method = request.POST.get("payment_method")


        date = request.POST.get("date")
        if date:
            stock.date = date

        stock.save()

        return redirect("stock")

    return render(request, "edit_stock.html", {"stock": stock})

def delete_stock(request, id):

    Stock.objects.filter(id=id).delete()

    return redirect("stock")


# EDIT SALES
def edit_sales(request, id):

    sale = get_object_or_404(Sale, id=id)

    if request.method == "POST":

        quantity = int(request.POST.get("quantity") or 0)
        unit_price = float(request.POST.get("unit_price") or 0)

        if quantity <= 0 or unit_price <= 0:
            return render(request, "edit_sales.html", {
                "sale": sale,
                "error": "Quantity and Unit Price must be greater than 0"
            })

        sale.item_name = request.POST.get("item_name")
        sale.quantity = quantity
        sale.unit_price = unit_price
        sale.total = quantity * unit_price

        sale.customer_name = request.POST.get("customer_name")
        sale.customer_contact = request.POST.get("customer_contact")
        sale.item_type = request.POST.get("item_type")
        sale.item_brand = request.POST.get("item_brand")

        # SAFE DATE HANDLING 
        date = request.POST.get("date")
        if date:
            sale.date = date

        sale.save()

        return redirect("sales")

    return render(request, "edit_sales.html", {
        "sale": sale
    })

def delete_sale(request, id):

    Sale.objects.filter(id=id).delete()

    return redirect("sales")



# EDIT DEPOSIT
def edit_deposit(request, id):

    deposit = get_object_or_404(Deposit, id=id)

    if request.method == "POST":

        deposit.amount = request.POST.get("amount")
        deposit.name = request.POST.get("name")
        deposit.phone = request.POST.get("phone")
        deposit.method = request.POST.get("method")
        deposit.item_name = request.POST.get("item_name")
        deposit.nin = request.POST.get("nin") or "N/A"
        deposit.date = request.POST.get("date")

        deposit.save()

        return redirect("deposit")

    return render(request, "edit_deposit.html", {
        "deposit": deposit
    })


def delete_deposit(request, id):

    Deposit.objects.filter(id=id).delete()

    return redirect("deposit")


# EDIT SUPPLIER
def edit_supplier(request, id):

    supplier = get_object_or_404(Supplier, id=id)

    if request.method == "POST":

        supplier.supplier_name = request.POST.get("supplier_name")
        supplier.date = request.POST.get("date")
        supplier.company = request.POST.get("company")
        supplier.contact = request.POST.get("contact")
        supplier.email = request.POST.get("email")
        supplier.location = request.POST.get("location")

        supplier.save()

        return redirect("supplier")

    return render(request, "edit_supplier.html", {
        "supplier": supplier
    })


def delete_supplier(request, id):

    supplier = get_object_or_404(Supplier, id=id)

    supplier.delete()

    return redirect("supplier")