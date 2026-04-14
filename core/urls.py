from django.conf import settings
from django.conf.urls.static import static
from django.urls import  path
from . import views


urlpatterns = [
    path("", views.home_page, name="home_page"),
    path("catalog", views.CatalogView.as_view(), name="catalog_page"),
    path("product/<slug:product_slug>", views.ProductPage.as_view(), name="product"),
    path("about", views.about_page, name="about_page"),
    path("contact", views.contact_page, name="contact_page"),
    path("order_page", views.OrderView.as_view(), name="order_page"),

    path("api/create_message/", views.contact_message, name="contact_message"),
    path("api/create_request/", views.CreateOrderView.as_view(), name="create_request"),
    path("api/download-waybill/<int:request_id>/", views.DownloadWaybillView.as_view(), name="download_waybill"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)