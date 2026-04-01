from django.urls import  path
from . import views


urlpatterns = [
    path("", views.home_page, name="home_page"),
    path("catalog", views.catalog_page, name="catalog_page"),
    path("about", views.about_page, name="about_page"),
    path("contact", views.contact_page, name="contact_page"),
    path("order_page", views.order_page, name="order_page"),
]
