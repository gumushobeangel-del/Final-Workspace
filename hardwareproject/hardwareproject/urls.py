"""
URL configuration for hardwareproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from hardwareapp import views


urlpatterns = [
    path('admin/', admin.site.urls),
    #this handles the index request
    path('', views.index, name='index'),
    path('log/', views.login_view, name='log'),
    path('sales/', views.sales, name='sales'),
    path('sign/', views.sign, name='sign'),
    path('stock/', views.stock_view, name='stock'),
    path('supplier/', views.suppliers, name='supplier'),
    path('dash/', views.dash, name='dash'),
    path('deposit/', views.deposit, name='deposit'),
    path('receipt/<int:id>/', views.receipt, name='receipt'),
    path('edit/<int:id>/', views.edit_stock, name='edit_stock'),
    path('delete/<int:id>/', views.delete_stock, name='delete_stock'),
    path('edit_sales/<int:id>/', views.edit_sales, name='edit_sales'),
    path('delete_sale/<int:id>/', views.delete_sale, name='delete_sale'),
    path('deposit/edit/<int:id>/', views.edit_deposit, name='edit_deposit'),
    path('deposit/delete/<int:id>/', views.delete_deposit, name='delete_deposit'),
    path('edit_supplier/<int:id>/', views.edit_supplier, name='edit_supplier'),
    path('delete_supplier/<int:id>/', views.delete_supplier, name='delete_supplier'),
         
]


