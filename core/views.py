from django.shortcuts import render
from django.views.generic import ListView
from .models import Product, Category


def home_page(request):
    return render(request, "core/index.html")

def catalog_page(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, "core/catalog.html", {"products": products, "categories": categories})

def about_page(request):
    return render(request, "core/about.html")

def contact_page(request):
    return render(request, "core/contact.html")

def order_page(request):
    return render(request, "core/order.html")

