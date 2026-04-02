from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *

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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    prepopulated_fields = {"slug": ('name', )}
    
    search_fields = ['name']  


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_picture', 'sku', 'name', 'category', 'price', 'is_active', 'created_at')
    list_display_links = ('sku', 'name') 
    list_editable = ('price', 'is_active') 
    
    list_filter = ('is_active', 'category', 'created_at', )
    search_fields = ['sku', 'name', 'description']  
    prepopulated_fields = {"slug": ('name', )}  
    readonly_fields = ('created_at', 'updated_at')  
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('sku', 'name', 'slug', 'category', 'image')
        }),
        ('Цена и статус', {
            'fields': ('price', 'is_active')
        }),
        ('Описания', {
            'fields': ('short_description', 'description'),
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    
    list_per_page = 25
    ordering = ('-created_at',) 
    date_hierarchy = 'created_at' 

    @admin.display(description="Фотография продукта", ordering='content')
    def product_picture(self, product: Product):
        if product.image:
            return mark_safe(f"<img src='{product.image.url}' width='150' height='150'>")
        return "Без фото"