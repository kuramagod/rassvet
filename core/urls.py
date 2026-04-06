from django.conf import settings
from django.conf.urls.static import static
from django.urls import  path
from . import views


urlpatterns = [
    path("", views.home_page, name="home_page"),
    path("catalog", views.catalog_page, name="catalog_page"),
    path("product/<slug:product_slug>", views.ProductPage.as_view(), name="product"),
    path("about", views.about_page, name="about_page"),
    path("contact", views.contact_page, name="contact_page"),
    path("api/create_message/", views.contact_message, name="contact_message"),
    path('api/download-waybill/<int:request_id>/', views.download_waybill, name='download_waybill'),
    path("order_page", views.order_page, name="order_page"),
    path("api/create_request/", views.create_request, name="create_request"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
