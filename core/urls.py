from django.urls import  path
from . import views


urlpatterns = [
    path("", views.home_page, name="home_page"),
    path("catalog", views.catalog_page, name="catalog_page"),
    path("product/<slug:product_slug>", views.ProductPage.as_view(), name="product"),
    path("about", views.about_page, name="about_page"),
    path("contact", views.contact_page, name="contact_page"),
    path("api/create_message/", views.contact_message, name="contact_message"),
    path("order_page", views.order_page, name="order_page"),
    path("api/create_request/", views.create_request, name="create_request"),
]
