from django.contrib import admin
from django.utils.safestring import mark_safe
from django.template.defaultfilters import truncatechars

from .models import *

admin.site.register(DeliveryType)

# Действия
@admin.action(description="Активировать выбранные товары")
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)

@admin.action(description="Деактивировать выбранные товары")
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)

# Inlines
class RequestItemInline(admin.TabularInline):
    model = RequestItem
    extra = 1
    readonly_fields = ('price', 'quantity')
    can_delete = True


class ProductCharacteristicInline(admin.TabularInline):
    model = ProductCharacteristic
    extra = 2


class ProductImagesInline(admin.TabularInline):
    model = ProductImages
    extra = 1
    fields = ('image', 'is_main')

# Админ таблицы
@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    inlines = [RequestItemInline]
    list_display = ('code', 'client',  'status', 'total_price', 'items_count', 'created_at')
    list_display_links = ('code', 'client', )
    list_editable = ('status', )
    
    list_filter = ('status', 'created_at', )
    search_fields = ['code', 'client__company_name', 'contact__fullname']  
    readonly_fields = ('created_at', ) 

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = "Кол-во позиций"

    list_per_page = 25
    ordering = ('-created_at',) 
    date_hierarchy = 'created_at'


@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ('product_image', 'product', 'is_main')
    list_display_links = ('product_image', 'product', )
    list_editable = ('is_main', )

    list_filter = ('is_main', )
    search_fields = ['product__sku', 'product__name'] 

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

    @admin.display(description="Фотография продукта", ordering='content')
    def product_image(self, obj: ProductImages):
        if obj.image and hasattr(obj.image, 'url'):
            return mark_safe(f"<img src='{obj.image.url}' width='150' height='150'>")
        return "Без фото"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    prepopulated_fields = {"slug": ('name', )}
    
    search_fields = ['name'] 


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'tin', 'legal_address', 'created_at')
    list_display_links = ('company_name', )

    list_filter = ('created_at', )
    search_fields = ['company_name', 'tin'] 

    list_per_page = 25
    ordering = ('-created_at',) 
    date_hierarchy = 'created_at' 


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'jobtitle', 'phone', 'email', 'client')
    list_display_links = ('fullname', )

    list_filter = ('client', )
    search_fields = ['fullname', 'phone', 'email', 'client__company_name']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('news_picture', 'title', 'truncated_description', 'created_at')
    list_display_links = ('news_picture', 'title')

    list_filter = ('created_at', )
    search_fields = ['title']

    list_per_page = 25
    ordering = ('-created_at',) 
    date_hierarchy = 'created_at'

    @admin.display(description="Описание")
    def truncated_description(self, obj):
        return truncatechars(obj.description, 50)

    @admin.display(description="Фотография новости", ordering='content')
    def news_picture(self, obj: News):
        if obj.image and hasattr(obj.image, 'url'):
            return mark_safe(f"<img src='{obj.image.url}' width='150' height='150'>")
        return "Без фото"


@admin.register(RequestStatus)
class RequestStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', )
    list_display_links = ('name', )


@admin.register(RequestItem)
class RequestItemAdmin(admin.ModelAdmin):
    list_display = ('request', 'product', 'price', 'quantity')
    list_display_links = ('request', ) 
    readonly_fields = ('price', )

    list_filter = ('request', 'product')
    search_fields = ['request', 'product__name', 'product__sku']  


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'truncated_text', 'created_at')
    list_display_links = ('name', )

    @admin.display(description="Текст сообщения")
    def truncated_text(self, obj):
        return truncatechars(obj.text, 50)

    search_fields = ['name']
    list_filter = ('created_at', )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_picture', 'sku', 'name', 'category', 'price', 'is_active', 'created_at')
    list_display_links = ('sku', 'name', 'product_picture') 
    list_editable = ('price', 'is_active') 
    inlines = [ProductCharacteristicInline, ProductImagesInline]
    actions = [make_active, make_inactive]
    
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
    def product_picture(self, obj: Product):
        if obj.image and hasattr(obj.image, 'url'):
            return mark_safe(f"<img src='{obj.image.url}' width='150' height='150'>")
        return "Без фото"
    

@admin.register(ProductCharacteristic)
class ProductCharacteristicAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'value')
    list_editable = ('value', )

    list_filter = ('product',  )
    search_fields = ['product__name', 'product__sku', 'name']  
