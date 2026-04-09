from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import Client, Contact, DeliveryType, Request, RequestStatus, RequestItem, Product

class OrderService:
    """Сервис для работы с заказами"""
    
    @staticmethod
    def validate_order_data(data):
        """Валидация данных заказа"""
        required_fields = ['company_name', 'inn', 'address', 'contact_person', 
                          'phone', 'email', 'delivery_type', 'items']
        
        errors = {}
        for field in required_fields:
            if not data.get(field):
                errors[field] = f'Поле {field} обязательно для заполнения'
        
        if not data.get('items'):
            errors['items'] = 'Добавьте хотя бы один товар'
            
        return errors
    
    @staticmethod
    def get_or_update_client(data):
        """Получение или обновление клиента"""
        inn = data['inn']
        client, created = Client.objects.get_or_create(
            tin=inn,
            defaults={
                'company_name': data['company_name'],
                'legal_address': data['address']
            }
        )
        
        if not created:
            # Обновляем данные только если они изменились
            updated = False
            if client.company_name != data['company_name']:
                client.company_name = data['company_name']
                updated = True
            if client.legal_address != data['address']:
                client.legal_address = data['address']
                updated = True
            if updated:
                client.save()
                
        return client
    
    @staticmethod
    def create_contact(data, client):
        """Создание контакта"""
        return Contact.objects.create(
            fullname=data['contact_person'],
            jobtitle=data.get('position', ''),
            phone=data['phone'],
            email=data['email'],
            client=client
        )
    
    @staticmethod
    def get_delivery_type(delivery_type_id):
        """Получение типа доставки"""
        try:
            return DeliveryType.objects.get(id=delivery_type_id)
        except DeliveryType.DoesNotExist:
            raise ValidationError('Указанный тип доставки не существует')
    
    @staticmethod
    def get_or_create_default_status():
        """Получение или создание статуса 'Новая'"""
        status, _ = RequestStatus.objects.get_or_create(
            code='new',
            defaults={'name': 'Новая'}
        )
        return status
    
    @staticmethod
    def create_request_items(request_obj, items_data):
        """Создание позиций заказа"""
        items = []
        total_price = 0
        invalid_products = []
        
        for item_data in items_data:
            try:
                product = Product.objects.get(
                    id=item_data['product_id'], 
                    is_active=True
                )
                
                quantity = item_data['quantity']
                price = product.price
                item_total = price * quantity
                
                request_item = RequestItem.objects.create(
                    request=request_obj,
                    product=product,
                    quantity=quantity,
                    price=price
                )
                
                items.append(request_item)
                total_price += item_total
                
            except Product.DoesNotExist:
                invalid_products.append(item_data.get('product_name', 'Неизвестный товар'))
        
        return items, total_price, invalid_products
    
    @classmethod
    def create_order(cls, data):
        """Основной метод создания заказа"""
        # Валидация
        errors = cls.validate_order_data(data)
        if errors:
            raise ValidationError(errors)
        
        with transaction.atomic():
            # Создание основных объектов
            client = cls.get_or_update_client(data)
            contact = cls.create_contact(data, client)
            delivery_type = cls.get_delivery_type(data['delivery_type'])
            status = cls.get_or_create_default_status()
            
            # Создание заявки
            request_obj = Request.objects.create(
                client=client,
                contact=contact,
                status=status,
                delivery_type=delivery_type,
                delivery_address=data.get('delivery_address', ''),
                comment=data.get('comments', ''),
                total_price=0
            )
            
            # Создание позиций
            items, total_price, invalid_products = cls.create_request_items(
                request_obj, data['items']
            )
            
            if invalid_products:
                raise ValidationError(
                    f'Следующие товары недоступны для заказа: {", ".join(invalid_products)}'
                )
            
            # Обновление суммы заказа
            request_obj.total_price = total_price
            request_obj.save()
            
            return request_obj