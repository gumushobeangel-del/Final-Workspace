from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout

from .models import Stock, Sale, Deposit, Receipt, Supplier,Register,Credit
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


# HOME


def index(request):
    return render(request, "index.html")

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect

def login_view(request):

    context = {}

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username:
            context["error_username"] = True

        if not password:
            context["error_password"] = True

        if context:
            return render(request, "log.html", context)

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)

            # ASSIGN ROLE
            if user.username.lower() == "angellina":
                request.session["role"] = "admin"

            elif user.username.lower() == "kevin":
                request.session["role"] = "sales"

            elif user.username.lower() == "alvin":
                request.session["role"] = "stock_manager"

            else:
                request.session["role"] = "user"

            request.session["username"] = user.username

            # REDIRECT BASED ON ROLE
            role = request.session["role"]

            if role == "admin":
                return redirect("dash")

            elif role == "sales":
                return redirect("sales")

            elif role == "stock_manager":
                return redirect("stock")

            else:
                return redirect("log")

        else:
            messages.error(request, "Wrong username or password")
            return redirect("log")

    return render(request, "log.html")



def sign(request):

    error = None

    users = {
        "admin": {"username": "Angellina", "password": "angel266"},
        "sales": {"username": "kevin", "password": "kevin256"},
        "stock_manager": {"username": "alvin", "password": "alvie233"},
    }

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        role = request.POST.get("role", "").strip()

        # STEP 1: check empty fields FIRST
        if not username or not password or not role:
            error = "All fields are required"

        # STEP 2: validate role
        elif role not in users:
            error = "Invalid role selected"

        else:
            stored_user = users[role]

            # STEP 3: username check
            if username.lower() != stored_user["username"].lower():
                error = "Wrong username"

            # STEP 4: password check
            elif password != stored_user["password"]:
                error = "Wrong password"

            else:
                request.session["role"] = role
                request.session["username"] = username

                return redirect({
                    "admin": "dash",
                    "sales": "sales",
                    "stock_manager": "stock"
                }[role])

    return render(request, "sign.html", {"error": error})
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect("log")
@login_required
def register(request):

    context = {}

    if request.method == "POST":

        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()

        if not name:
            context["error_name"] = True

        if not phone:
            context["error_phone"] = True

        if not email:
            context["error_email"] = True

        if not address:
            context["error_address"] = True

        if context:
            customers = Register.objects.all().order_by('-id')
            context["customers"] = customers
            return render(request, "register.html", context)

        Register.objects.create(
            name=name,
            phone=phone,
            email=email,
            address=address
        )

        return redirect('register')

    customers = Register.objects.all().order_by('-id')

    return render(request, 'register.html', {
        'customers': customers
    })
@login_required
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

@login_required
def delete_customer(request, id):
    customer = get_object_or_404(Register, id=id)
    customer.delete()
    return redirect("register")


#login
from django.contrib import messages
from django.shortcuts import render, redirect


# DASHBOARD
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from datetime import datetime, timedelta

from .models import Stock, Sale, Supplier

@login_required
def dash(request):
    role = request.session.get("role")

    # BLOCK NON-ADMINS
    if role != "admin":#if user not admin send them away
        return redirect("sign") 

    # TOTAL PRODUCTS
    total_products = Stock.objects.count()#count the records

    # LOW STOCK
    low_stock = Stock.objects.filter(quantity__lt=20).count()#select specific records if less tha 20 low stock

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
from datetime import datetime, date, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def stock_view(request):

    role = request.session.get("role")

    if role not in ["admin", "stock_manager"]:
        return redirect("sign")

    stocks = Stock.objects.all()
    errors = {}

    if request.method == "POST":

        item_name = request.POST.get("item_name", "").strip()
        quantity = request.POST.get("quantity", "").strip()
        unit_cost = request.POST.get("unit_cost", "").strip()
        unit_price = request.POST.get("unit_price", "").strip()
        stock_date_str = request.POST.get("date", "").strip()
        category = request.POST.get("category", "").strip()
        payment_method = request.POST.get("payment_method", "").strip()

        # VALIDATION
        if not item_name:
            errors["item_name"] = "Item name is required"

        if not quantity:
            errors["quantity"] = "Quantity is required"

        if not unit_cost:
            errors["unit_cost"] = "Unit cost is required"

        if not unit_price:
            errors["unit_price"] = "Unit price is required"

        if not stock_date_str:
            errors["date"] = "Date is required"

        if not category:
            errors["category"] = "Category is required"

        if not payment_method:
            errors["payment_method"] = "Payment method is required"

        # stop if missing fields
        if errors:
            return render(request, "stock.html", {
                "stocks": stocks,
                "errors": errors
            })

        # convert safely
        try:
            quantity = int(quantity)
            unit_cost = float(unit_cost)
            unit_price = float(unit_price)
        except:
            errors["numbers"] = "Enter valid numeric values"
            return render(request, "stock.html", {
                "stocks": stocks,
                "errors": errors
            })

        # prevent negatives
        if quantity <= 0:
            errors["quantity"] = "Quantity must be greater than zero"
        if unit_cost <= 0:
            errors["unit_cost"] = "Unit cost must be greater than zero"
        if unit_price <= 0:
            errors["unit_price"] = "Unit price must be greater than zero"

        if errors:
            return render(request, "stock.html", {
                "stocks": stocks,
                "errors": errors
            })

        # date validation
        try:
            stock_date = datetime.strptime(stock_date_str, "%Y-%m-%d").date()
        except:
            errors["date"] = "Invalid date format"
            return render(request, "stock.html", {
                "stocks": stocks,
                "errors": errors
            })

        today = date.today()
        one_week_ago = today - timedelta(days=7)

        if stock_date > today:
            errors["date"] = "Future dates are not allowed"

        if stock_date < one_week_ago:
            errors["date"] = "Date cannot be older than 7 days"

        if errors:
            return render(request, "stock.html", {
                "stocks": stocks,
                "errors": errors
            })

        # SAVE STOCK
        stock_item, created = Stock.objects.get_or_create(
            item_name=item_name,
            defaults={
                "quantity": quantity,
                "unit_cost": unit_cost,
                "unit_price": unit_price,
                "date": stock_date,
                "category": category,
                "payment_method": payment_method
            }
        )

        if not created:
            stock_item.quantity += quantity
            stock_item.unit_cost = unit_cost
            stock_item.unit_price = unit_price
            stock_item.date = stock_date
            stock_item.save()

        messages.success(request, "Stock saved successfully!")
        return redirect("stock")

    return render(request, "stock.html", {
        "stocks": stocks,
        "errors": {}
    })

# SALES
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, date
from django.contrib.auth.decorators import login_required
import re

from .models import Stock, Sale


@login_required
def sales(request):

    errors = {}

    if request.method == "POST":

        stock_id = request.POST.get("stock_id", "").strip()
        quantity = request.POST.get("quantity", "").strip()
        unit_price = request.POST.get("unit_price", "").strip()
        distance = request.POST.get("distance_km", "").strip()
        sale_date_str = request.POST.get("date", "").strip()
        customer_name = request.POST.get("customer_name", "").strip()
        customer_contact = request.POST.get("customer_contact", "").strip()
        item_type = request.POST.get("item_type", "").strip()
        item_brand = request.POST.get("item_brand", "").strip()

        # REQUIRED FIELDS
        if not stock_id:
            errors["stock"] = "Please select an item"

        if not quantity:
            errors["quantity"] = "Quantity is required"

        if not unit_price:
            errors["price"] = "Unit price is required"

        if not distance:
            errors["distance"] = "Distance is required"

        if not sale_date_str:
            errors["date"] = "Date is required"

        if not customer_name:
            errors["customer"] = "Customer name is required"

        if not customer_contact:
            errors["contact"] = "Customer contact is required"

        if not item_type:
            errors["type"] = "Item type is required"

        if not item_brand:
            errors["brand"] = "Item brand is required"

        # PHONE VALIDATION
        phone_pattern = r"^\+256[0-9]{9}$"
        if customer_contact and not re.match(phone_pattern, customer_contact):
            errors["contact"] = "Invalid phone number (+256XXXXXXXXX)"

        try:
            quantity = int(quantity)
            if quantity <= 0:
                errors["quantity"] = "Quantity must be greater than 0"
        except:
            if "quantity" not in errors:
                errors["quantity"] = "Enter a valid quantity"

        try:
            unit_price = float(unit_price)
            if unit_price <= 0:
                errors["price"] = "Unit price must be greater than 0"
        except:
            if "price" not in errors:
                errors["price"] = "Enter a valid unit price"

        try:
            distance = float(distance)
            if distance < 0:
                errors["distance"] = "Distance cannot be negative"
        except:
            if "distance" not in errors:
                errors["distance"] = "Enter a valid distance"

        # DATE VALIDATION (FIXED)
        try:
            sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d").date()
            today = date.today()

            if sale_date > today:
                errors["date"] = "Future sales are not allowed"

        except:
            if "date" not in errors:
                errors["date"] = "Invalid date format"

        # STOP IF ERRORS EXIST
        if errors:
            return render(request, "sales.html", {
                "errors": errors,
                "stocks": Stock.objects.all().order_by("-id"),
                "sales": Sale.objects.all().order_by("-id")
            })

        # STOCK CHECK
        stock = get_object_or_404(Stock, id=stock_id)

        if stock.quantity < quantity:
            messages.error(request, "Not enough stock available")
            return redirect("sales")

        # UPDATE STOCK
        stock.quantity -= quantity
        stock.save()

        # CALCULATIONS
        subtotal = quantity * unit_price
        transport = 0 if (distance <= 10 and subtotal >= 500000) else 30000
        grand_total = subtotal + transport

        # SAVE SALE
        Sale.objects.create(
            item_name=stock.item_name,
            quantity=quantity,
            unit_price=unit_price,
            total=subtotal,
            distance_km=distance,
            transport=transport,
            grand_total=grand_total,
            customer_name=customer_name,
            customer_contact=customer_contact,
            item_type=item_type,
            item_brand=item_brand,
            date=sale_date
        )

        messages.success(request, "Sale recorded successfully!")
        return redirect("sales")

    return render(request, "sales.html", {
        "errors": {},
        "stocks": Stock.objects.all().order_by("-id"),
        "sales": Sale.objects.all().order_by("-id")
    })


def deposit(request):

    if request.method == "POST":

        amount = float(request.POST.get("amount") or 0)
    
#Deposit

ITEM_PRICES = {
    "Cement": 30000,
    "Glass": 15000,
    "Iron Sheets": 20000,
    "Iron Bars": 27000,
}

@login_required
def deposit(request):

    if request.method == "POST":

        amount = float(request.POST.get("amount") or 0)
        quantity = int(request.POST.get("quantity") or 0)
        item_name = request.POST.get("item_name")
        deposit_date_str = request.POST.get("date")

        # prevents negatives
        if amount <= 0 or quantity <= 0:
            messages.error(request, "Amount and quantity must be greater than 0")
            return redirect("deposit")

        # validate item
        price = ITEM_PRICES.get(item_name)
        if not price:
            messages.error(request, "Invalid item selected")
            return redirect("deposit")

        # date validation
        try:
            deposit_date = datetime.strptime(deposit_date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            messages.error(request, "Invalid date format")
            return redirect("deposit")

        today = date.today()
        one_week_ago = today - timedelta(days=7)

        # block future dates
        if deposit_date > today:
            messages.error(request, "Future dates are not allowed")
            return redirect("deposit")

        # block old dates
        if deposit_date < one_week_ago:
            messages.error(request, "Date is too old (must be within 7 days)")
            return redirect("deposit")

        # calculations
        total_cost = price * quantity
        balance = total_cost - amount

        if balance < 0:
            balance = 0

        Deposit.objects.create(
            amount=amount,
            quantity=quantity,
            balance=balance,
            name=request.POST.get("name"),
            phone=request.POST.get("phone"),
            method=request.POST.get("method"),
            item_name=item_name,
            nin=request.POST.get("nin") or "N/A",
            date=deposit_date
        )

        messages.success(request, "Deposit recorded successfully")
        return redirect("deposit")

    deposits = Deposit.objects.all().order_by("-id")

    return render(request, "deposit.html", {
        "deposits": deposits
    })
# RECEIPT


@login_required
def receipt(request, id):
    sale = get_object_or_404(Sale, id=id)
    return render(request, "receipt.html", {"sale": sale})


# SUPPLIERS

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Supplier
import re


@login_required
def suppliers(request):

    errors = {}

    if request.method == "POST":

        supplier_name = request.POST.get("supplier_name", "").strip()
        company = request.POST.get("company", "").strip()
        contact = request.POST.get("contact", "").strip()
        email = request.POST.get("email", "").strip()
        location = request.POST.get("location", "").strip()

        # REQUIRED VALIDATION
        if not supplier_name:
            errors["supplier_name"] = "Supplier name is required"

        if not company:
            errors["company"] = "Company is required"

        if not contact:
            errors["contact"] = "Contact is required"

        if not email:
            errors["email"] = "Email is required"

        if not location:
            errors["location"] = "Location is required"

        # CONTACT VALIDATION (STRICT 13 CHAR RULE)
        if contact:
            if len(contact) != 13:
                errors["contact"] = "Contact must be exactly 13 characters"

            elif not re.match(r"^\+256[0-9]{9}$", contact):
                errors["contact"] = "Contact must start with +256 and have 9 digits after"

        # EMAIL VALIDATION
        if email and "@" not in email:
            errors["email"] = "Enter a valid email address"

        # SAVE ONLY IF NO ERRORS
        if not errors:

            Supplier.objects.create(
                supplier_name=supplier_name,
                company=company,
                contact=contact,
                email=email,
                location=location,
            )

            messages.success(request, "Supplier added successfully!")
            return redirect("supplier")

    suppliers = Supplier.objects.all().order_by("-id")

    return render(request, "suppliers.html", {
        "suppliers": suppliers,
        "errors": errors
    })

# EDIT STOCK


@login_required
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



# EDIT SALES
@login_required
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

        # GET STOCK ITEM
        stock = get_object_or_404(Stock, item_name=sale.item_name)

        # RETURN OLD QUANTITY BACK TO STOCK
        stock.quantity += sale.quantity

        # CHECK IF NEW QUANTITY IS AVAILABLE
        if stock.quantity < quantity:
            return render(request, "edit_sales.html", {
                "sale": sale,
                "error": "Not enough stock available!"
            })

        # DEDUCT NEW QUANTITY
        stock.quantity -= quantity
        stock.save()

        # UPDATE SALE
        sale.item_name = request.POST.get("item_name")
        sale.quantity = quantity
        sale.unit_price = unit_price

        # RECALCULATE TOTAL 
        sale.total = quantity * unit_price

        sale.customer_name = request.POST.get("customer_name")
        sale.customer_contact = request.POST.get("customer_contact")
        sale.item_type = request.POST.get("item_type")
        sale.item_brand = request.POST.get("item_brand")

        date = request.POST.get("date")
        if date:
            sale.date = date

        sale.save()

        return redirect("sales")

    return render(request, "edit_sales.html", {
        "sale": sale
    })

@login_required
def delete_sale(request, id):

    # BLOCK NON-ADMIN USERS
    if request.session.get("role") != "admin":
        return redirect("sales")  # or show error page

    sale = get_object_or_404(Sale, id=id)
    sale.delete()

    return redirect("sales")


# EDIT DEPOSIT
@login_required
def edit_deposit(request, id):
    deposit = get_object_or_404(Deposit, id=id)

    if request.method == "POST":

        deposit.name = request.POST.get("name")
        deposit.phone = request.POST.get("phone")

        new_amount = float(request.POST.get("amount") or 0)
        new_quantity = int(request.POST.get("quantity") or 0)
        item_name = request.POST.get("item_name")

        deposit.method = request.POST.get("method")
        deposit.nin = request.POST.get("nin")
        deposit.item_name = item_name

        #GET PRICE AGAIN
        price = ITEM_PRICES.get(item_name, 0)

        #RECALCULATE TOTAL
        total_cost = price * new_quantity

        #NEW BALANCE
        deposit.amount = new_amount
        deposit.quantity = new_quantity
        deposit.balance = total_cost - new_amount   

        if deposit.balance < 0:
            deposit.balance = 0

        date = request.POST.get("date")
        if date:
            deposit.date = date

        deposit.save()

        return redirect("deposit")

    return render(request, "edit_deposit.html", {"deposit": deposit})

@login_required
def delete_deposit(request, id):

    Deposit.objects.filter(id=id).delete()

    return redirect("deposit")


# EDIT SUPPLIER
@login_required
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

@login_required
def delete_supplier(request, id):

    supplier = get_object_or_404(Supplier, id=id)

    supplier.delete()

    return redirect("supplier")

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.utils import timezone
from .models import Credit


@login_required
def credit(request):

    errors = {}

    if request.method == "POST":

        supplier_name = request.POST.get("supplier_name", "").strip()
        item_name = request.POST.get("item_name", "").strip()
        quantity_raw = request.POST.get("quantity", "").strip()
        unit_price_raw = request.POST.get("unit_price", "").strip()
        amount_paid_raw = request.POST.get("amount_paid", "").strip()
        date_str = request.POST.get("date", "").strip()

        # REQUIRED FIELDS
        if not supplier_name:
            errors["supplier_name"] = "Supplier name is required"

        if not item_name:
            errors["item_name"] = "Item name is required"

        if not quantity_raw:
            errors["quantity"] = "Quantity is required"

        if not unit_price_raw:
            errors["unit_price"] = "Unit price is required"

        if not date_str:
            errors["date"] = "Date is required"

        # DEFAULTS
        quantity = None
        unit_price = None
        amount_paid = 0

        # VALIDATE QUANTITY
        if quantity_raw:
            try:
                quantity = int(quantity_raw)
                if quantity <= 0:
                    errors["quantity"] = "Quantity must be greater than 0"
            except:
                errors["quantity"] = "Enter a valid quantity"

        # VALIDATE UNIT PRICE
        if unit_price_raw:
            try:
                unit_price = float(unit_price_raw)
                if unit_price <= 0:
                    errors["unit_price"] = "Unit price must be greater than 0"
            except:
                errors["unit_price"] = "Enter a valid unit price"

        # VALIDATE AMOUNT PAID
        if amount_paid_raw:
            try:
                amount_paid = float(amount_paid_raw)
                if amount_paid < 0:
                    errors["amount_paid"] = "Amount paid cannot be negative"
            except:
                errors["amount_paid"] = "Enter a valid amount"

        # DATE VALIDATION (FIXED PROPERLY HERE)
        credit_date = None

        if date_str:
            credit_date = parse_date(date_str)
            today = timezone.localdate()

            if not credit_date:
                errors["date"] = "Invalid date selected"

            elif credit_date > today:
                errors["date"] = "Future dates are not allowed"

        # SAVE ONLY IF VALID
        if not errors and credit_date:

            Credit.objects.create(
                supplier_name=supplier_name,
                item_name=item_name,
                quantity=quantity,
                unit_price=unit_price,
                amount_paid=amount_paid,
                date=credit_date
            )

            messages.success(request, "Credit record added successfully!")
            return redirect("credit")

    credits = Credit.objects.all().order_by("-id")

    return render(request, "credit.html", {
        "credits": credits,
        "errors": errors
    })

@login_required
def delete_supplier_credit(request, id):
    credit = get_object_or_404(Credit, id=id)
    credit.delete()

    return redirect("credit")  

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from .models import Credit

@login_required
def edit_supplier_credit(request, id):

    credit = get_object_or_404(Credit, id=id)

    if request.method == "POST":

        supplier_name = request.POST.get("supplier_name", "").strip()
        item_name = request.POST.get("item_name", "").strip()
        quantity = request.POST.get("quantity", "").strip()
        unit_price = request.POST.get("unit_price", "").strip()
        amount_paid = request.POST.get("amount_paid", "").strip()
        date_str = request.POST.get("date", "").strip()

        errors = {}

        # VALIDATION
        if not supplier_name:
            errors["supplier_name"] = "Supplier name is required"

        if not item_name:
            errors["item_name"] = "Item name is required"

        # quantity
        try:
            quantity = int(quantity)
            if quantity <= 0:
                errors["quantity"] = "Quantity must be greater than 0"
        except:
            errors["quantity"] = "Invalid quantity"

        # unit price
        try:
            unit_price = float(unit_price)
            if unit_price <= 0:
                errors["unit_price"] = "Unit price must be greater than 0"
        except:
            errors["unit_price"] = "Invalid unit price"

        # amount paid
        try:
            amount_paid = float(amount_paid or 0)
            if amount_paid < 0:
                errors["amount_paid"] = "Amount paid cannot be negative"
        except:
            errors["amount_paid"] = "Invalid amount paid"

        # DATE (FIXED)
        credit_date = parse_date(date_str)

        if not credit_date:
            errors["date"] = "Invalid date selected"

        # SAVE ONLY IF NO ERRORS
        if not errors:

            credit.supplier_name = supplier_name
            credit.item_name = item_name
            credit.quantity = quantity
            credit.unit_price = unit_price
            credit.amount_paid = amount_paid
            credit.date = credit_date

            credit.save()

            messages.success(request, "Credit updated successfully!")
            return redirect("credit")

        # if errors → show form again
        return render(request, "edit_credit.html", {
            "credit": credit,
            "errors": errors
        })

    return render(request, "edit_credit.html", {
        "credit": credit
    })


@login_required
def supplier_credit_receipt(request, id):
    credit = get_object_or_404(Credit, id=id)

    return render(request, "credit_receipt.html", {
        "credit": credit,
        "print_now": True
    })

# DEPOSIT RECEIPT
@login_required
def deposit_receipt(request, id):
    deposit = get_object_or_404(Deposit, id=id)

    return render(request, "deposit_receipt.html", {
        "deposit": deposit,
        "print_now": True
    })


from decimal import Decimal
from django.db.models import Sum
@login_required
def reports(request):
    # GET VALUES
    total_sales = Sale.objects.aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    total_stock = Stock.objects.count()
    total_customers = Register.objects.count()
    total_deposits = Deposit.objects.aggregate(Sum('amount'))['amount__sum'] or 0

    total_items = Sale.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0

    total_cost = Stock.objects.aggregate(Sum('unit_cost'))['unit_cost__sum'] or 0

    # FORCE SAME TYPE 
    total_sales = Decimal(str(total_sales))
    total_cost = Decimal(str(total_cost))

    # CALCULATE PROFIT
    profit = total_sales - total_cost#gets the profit

    recent_sales = Sale.objects.all().order_by('-id')[:5]

    context = {
        'total_sales': total_sales,
        'total_stock': total_stock,
        'total_customers': total_customers,
        'total_deposits': total_deposits,
        'profit': profit,
        'total_items': total_items,
        'recent_sales': recent_sales,
    }

    return render(request, 'reports.html', context)



