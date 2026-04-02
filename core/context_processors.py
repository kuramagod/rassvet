from .models import Product

def footer_products(request):
    products = Product.objects.filter(is_active=True)[:5]
    return {"footer_products": products}