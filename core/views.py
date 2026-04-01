from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Product, Category, News, Message, DeliveryType, Client, Contact, RequestStatus, Request, RequestItem


def home_page(request):
    products = Product.objects.filter(is_active=True)[:3]   
    news = News.objects.all() 
    return render(request, "core/index.html", {"products": products, "news": news})

def catalog_page(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    return render(request, "core/catalog.html", {"products": products, "categories": categories})

def about_page(request):
    return render(request, "core/about.html")

def contact_page(request):
    return render(request, "core/contact.html")

@require_POST
def contact_message(request):
    try:
        data = json.loads(request.body)

        name = data.get("username")
        contact = data.get("contact")
        text = data.get("message")

        email = ""
        phone = ""

        if "@" in contact:
            email = contact
        else:
            phone = contact
        
        Message.objects.create(
            name=name,
            email=email,
            phone=phone,
            text=text
        )

        return JsonResponse({"status": "ok"})
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def order_page(request):
    delivery_types = DeliveryType.objects.all()
    products = Product.objects.filter(is_active=True)
    return render(request, "core/order.html", {"delivery_types": delivery_types, 'products': products})

@require_POST
@csrf_exempt
def create_request(request):
    try:
        data = json.loads(request.body)
        
        required_fields = ['company_name', 'inn', 'address', 'contact_person', 
                          'phone', 'email', 'delivery_type', 'items']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False,
                    'error': f'Поле {field} обязательно для заполнения'
                }, status=400)
        
        if len(data['items']) == 0:
            return JsonResponse({
                'success': False,
                'error': 'Добавьте хотя бы один товар'
            }, status=400)
        
        with transaction.atomic():
            # Создаем или получаем клиента по ИНН
            inn = data['inn']
            try:
                client = Client.objects.get(tin=inn)
                # Обновляем данные клиента, если они изменились
                if client.company_name != data['company_name']:
                    client.company_name = data['company_name']
                if client.legal_address != data['address']:
                    client.legal_address = data['address']
                client.save()
            except Client.DoesNotExist:
                client = Client.objects.create(
                    company_name=data['company_name'],
                    tin=inn,
                    legal_address=data['address']
                )
            
            # Создаем контактное лицо
            contact = Contact.objects.create(
                fullname=data['contact_person'],
                jobtitle=data.get('position', ''),
                phone=data['phone'],
                email=data['email'],
                client=client
            )
            
            # Получаем тип доставки
            try:
                delivery_type = DeliveryType.objects.get(id=data['delivery_type'])
            except DeliveryType.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Указанный тип доставки не существует'
                }, status=400)
            
            # Получаем статус "Новая"
            try:
                status = RequestStatus.objects.get(code='new')
            except RequestStatus.DoesNotExist:
                # Если статуса нет, создаем его
                status = RequestStatus.objects.create(
                    name='Новая',
                    code='new'
                )
            
            # Создаем заявку
            request_obj = Request.objects.create(
                client=client,
                contact=contact,
                status=status,
                delivery_type=delivery_type,
                delivery_address=data.get('delivery_address', ''),
                comment=data.get('comments', ''),
                total_price=0 
            )
            
            total_price = 0
            invalid_products = []
            
            # Создаем позиции заявки
            for item_data in data['items']:
                try:
                    # Проверяем, что продукт существует и активен
                    product = Product.objects.get(
                        id=item_data['product_id'], 
                        is_active=True
                    )
                    
                    price = product.price
                    quantity = item_data['quantity']
                    item_total = price * quantity
                    
                    # Создаем позицию
                    request_item = RequestItem.objects.create(
                        request=request_obj,
                        product=product,
                        quantity=quantity,
                        price=price
                    )
                    total_price += item_total
                    
                except Product.DoesNotExist:
                    # Если товар не найден или не активен, добавляем в список ошибок
                    invalid_products.append(item_data.get('product_name', 'Неизвестный товар'))
            
            # Если есть невалидные товары, откатываем транзакцию и возвращаем ошибку
            if invalid_products:
                return JsonResponse({
                    'success': False,
                    'error': f'Следующие товары недоступны для заказа: {", ".join(invalid_products)}'
                }, status=400)
            
            request_obj.total_price = total_price
            request_obj.save()
        
        return JsonResponse({
            'success': True,
            'order_number': request_obj.code,
            'message': f'Заявка #{request_obj.code} успешно создана'
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат данных'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)