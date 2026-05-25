from django.contrib import admin
from django.urls import path
from hardwareapp import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home
    path('', views.index, name='index'),

    # Auth
    path('log/', views.login_view, name='log'),
    path('sign/', views.sign, name='sign'),
    path('register/', views.register, name='register'), 

    path('customer/edit/<int:id>/', views.edit_customer, name='edit_customer'),
    path('customer/delete/<int:id>/', views.delete_customer, name='delete_customer'),

    # Core pages
    path('sales/', views.sales, name='sales'),
    path('stock/', views.stock_view, name='stock'),
    path('supplier/', views.suppliers, name='supplier'),
    path('dash/', views.dash, name='dash'),
    path('credit/', views.credit, name='credit'),
    path('reports/', views.reports, name='reports'),

    # Transactions
    path('deposit/', views.deposit, name='deposit'),
    path('receipt/<int:id>/', views.receipt, name='receipt'),

    # Stock actions
    path('edit/<int:id>/', views.edit_stock, name='edit_stock'),
 

    # Sales actions
    path('edit_sales/<int:id>/', views.edit_sales, name='edit_sales'),
    path('delete_sale/<int:id>/', views.delete_sale, name='delete_sale'),

    # Deposit actions
    path('deposit/edit/<int:id>/', views.edit_deposit, name='edit_deposit'),
    path('deposit/delete/<int:id>/', views.delete_deposit, name='delete_deposit'),

    # Supplier actions
    path('edit_supplier/<int:id>/', views.edit_supplier, name='edit_supplier'),
    path('delete_supplier/<int:id>/', views.delete_supplier, name='delete_supplier'),

    # Credit actions
    path('credit/edit/<int:id>/', views.edit_supplier_credit, name='edit_supplier_credit'),
    path('credit/delete/<int:id>/', views.delete_supplier_credit, name='delete_supplier_credit'),

    path('credit/receipt/<int:id>/', views.supplier_credit_receipt, name='supplier_credit_receipt'),

    path('deposit-receipt/<int:id>/', views.deposit_receipt, name='deposit_receipt'),

    

]

   