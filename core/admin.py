from django.contrib import admin

from .models import *

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductCharacteristic)
admin.site.register(ProductImages)
admin.site.register(DeliveryType)
admin.site.register(RequestStatus)
admin.site.register(Client)
admin.site.register(Contact)
admin.site.register(Request)
admin.site.register(RequestItem)
admin.site.register(Message)
admin.site.register(News)
