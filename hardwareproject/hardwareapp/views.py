from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login

from .models import Stock, Sale, Deposit, Receipt, Supplier


# HOME


def index(request):
    return render(request, "index.html")


def sign(request):
    if request.method == "POST":
        role = request.POST.get("role")

        if role == "admin":
            return redirect("dash")

        elif role == "sales":
            return redirect("sales")

        elif role == "stock_manager":
            return redirect("stock")

    return render(request, "sign.html")



# LOGIN


def login_view(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user:
            login(request, user)
            return redirect("dash")

    return render(request, "log.html")



# DASHBOARD
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from datetime import datetime, timedelta

from .models import Stock, Sale, Supplier


def dash(request):
    # TOTAL PRODUCTS
    total_products = Stock.objects.count()

    # LOW STOCK
    low_stock = Stock.objects.filter(quantity__lt=20).count()

    # SUPPLIERS
    suppliers = Supplier.objects.count()

    # TOTAL SALES
    total_sales = Sale.objects.aggregate(total=Sum('total'))['total'] or 0

    # DATES
    today = datetime.today().date()
    week = today - timedelta(days=7)
    month = today.replace(day=1)

    # TODAY SALES (FIXED - NO __date!)
    today_sales = Sale.objects.filter(date=today).aggregate(total=Sum('total'))['total'] or 0

    # WEEK SALES
    week_sales = Sale.objects.filter(date__gte=week).aggregate(total=Sum('total'))['total'] or 0

    # MONTH SALES
    month_sales = Sale.objects.filter(date__gte=month).aggregate(total=Sum('total'))['total'] or 0

    # TOP PRODUCT
    top_product = (
        Sale.objects.values('item_name')
        .annotate(total_qty=Sum('quantity'))
        .order_by('-total_qty')
        .first()
    )

    # STOCK LIST
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
        item_name = request.POST.get("item_name")
        quantity = int(request.POST.get("quantity") or 0)
        unit_price = float(request.POST.get("unit_price") or 0)

        total = quantity * unit_price#calculates automatically

        #stops users from entering negative values
        if quantity <= 0 or unit_price <= 0:
            return render(request, "sales.html", {
                "error": "Quantity and Unit Price must be greater than 0"
            })

        # GET STOCK
        stock = get_object_or_404(Stock, item_name=item_name)

        # CHECK STOCK
        if stock.quantity < quantity:#this will unable sales from entering when he enter the stock beyond
            return render(request, "sales.html", {
                "error": "Not enough stock available!"
            })

        # REDUCE STOCK
        stock.quantity -= quantity#this reduces stock
        stock.save()

        # SAVE SALE (ONLY ONCE)
        Sale.objects.create(
            item_name=item_name,
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

    # GET REQUEST → SHOW PAGE
    sales = Sale.objects.all().order_by('-id')
    return render(request, "sales.html", {"sales": sales})

#Deposit
def deposit(request):

    if request.method == "POST":

        amount = float(request.POST.get("amount") or 0)

        # Prevent negative values
        if amount <= 0:
            return render(request, "deposit.html", {
                "error": "Amount must be greater than 0"
            })


        Deposit.objects.create(
            amount=request.POST.get("amount"),
            name=request.POST.get("name"),
            phone=request.POST.get("phone"),
            method=request.POST.get("method"),
            item_name=request.POST.get("item_name"),
            nin=request.POST.get("nin") or "N/A",
            date=request.POST.get("date")
        )

        return redirect("deposit")

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

        # FIX DATE ISSUE
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

        sale.item_name = request.POST.get("item_name")
        sale.quantity = quantity
        sale.unit_price = unit_price
        sale.total = quantity * unit_price

        sale.customer_name = request.POST.get("customer_name")
        sale.customer_contact = request.POST.get("customer_contact")
        sale.item_type = request.POST.get("item_type")
        sale.item_brand = request.POST.get("item_brand")
        sale.date = request.POST.get("date")

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