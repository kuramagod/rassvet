import json
import os

from django.conf import settings
from django.db import transaction
from django.http import FileResponse, Http404, JsonResponse
from django.core.mail import EmailMessage
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic import DetailView

from .models import Category, Client, Contact, DeliveryType, Message, News, Product, Request, RequestItem, RequestStatus
from .utils import generate_waybill


def home_page(request):
    products = Product.objects.filter(is_active=True)[:3]   
    news = News.objects.all() 
    return render(request, "core/index.html", {"products": products, "news": news})

def catalog_page(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    return render(request, "core/catalog.html", {"products": products, "categories": categories})

class ProductPage(DetailView):
    model = Product
    template_name = "core/product.html"
    slug_url_kwarg = "product_slug"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['characteristics'] = self.get_object().characteristics.all()
        return context


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

        return JsonResponse({'success': True},  status=201)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def order_page(request):
    delivery_types = DeliveryType.objects.all()
    products = Product.objects.filter(is_active=True)
    return render(request, "core/order.html", {"delivery_types": delivery_types, 'products': products})

def send_invoice_email(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'invoices', f'nakladnaya_{request.id}.docx')
    
    email = EmailMessage(
        subject=f"Новая заявка {request.code}",
        body=f"Поступила новая заявка от {request.client.company_name}",
        to=["rassvet-info-vlg@mail.ru"]
    )

    email.attach_file(file_path)
    email.send(fail_silently=False)

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
            
            # Создание накладной
            file_url = generate_waybill(request_obj)

            send_invoice_email(request_obj)
        
        return JsonResponse({
            'success': True,
            'order_number': request_obj.code,
            'request_id': request_obj.id,
            'download_url': f'/api/download-waybill/{request_obj.id}/',
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


@require_http_methods(["GET"])
def download_waybill(request, request_id):
    try:
        
        try:
            request_obj = Request.objects.get(id=request_id)
        except Request.DoesNotExist:
            raise Http404("Заявка не найдена")
        
        # Формируем путь к файлу
        file_name = f"nakladnaya_{request_id}.docx"
        file_path = os.path.join(settings.MEDIA_ROOT, "invoices", file_name)
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            # Если файла нет - генерируем заново
            generate_waybill(request_obj)
            
            # Проверяем еще раз
            if not os.path.exists(file_path):
                raise Http404("Файл накладной не найден")
        
        # Открываем файл и отправляем на скачивание
        file = open(file_path, 'rb')
        response = FileResponse(
            file,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            filename=f'Накладная_{request_obj.code}_{request_id}.docx'
        )
        
        # Закрываем файл после отправки
        response['Content-Length'] = os.path.getsize(file_path)
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка при скачивании файла: {str(e)}'
        }, status=500)