from django.shortcuts import render


def home_page(request):
    return render(request, "core/index.html")

def catalog_page(request):
    return render(request, "core/catalog.html")

def about_page(request):
    return render(request, "core/about.html")

def contact_page(request):
    return render(request, "core/contact.html")

def order_page(request):
    return render(request, "core/order.html")

