from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

@receiver(post_migrate)
def create_initial_data(sender, **kwargs):
    if sender.name != 'core':
        return
    

    DeliveryType = apps.get_model('core', 'DeliveryType')
    RequestStatus = apps.get_model('core', 'RequestStatus')

    if DeliveryType.objects.exists() and RequestStatus.objects.exists():
        print("Начальные данные уже существуют, пропускаем инициализацию")
        return
    
    delivery_types = [
        {'name': 'Доставка транспортом поставщика'},
        {'name': 'Самовывоз'},
    ]
    
    for dt_data in delivery_types:
        obj, created = DeliveryType.objects.get_or_create(name=dt_data['name'])
        if created:
            created_count += 1
            print(f"Создан тип доставки: {dt_data['name']}")
        else:
            print(f"Тип доставки уже существует: {dt_data['name']}")
    
    
    statuses = [
        {'name': 'Новая', 'code': 'new'},
        {'name': 'В обработке', 'code': 'processing'},
        {'name': 'Подтверждена', 'code': 'confirmed'},
        {'name': 'Отгружена', 'code': 'shipped'},
        {'name': 'Отменена', 'code': 'cancelled'},
    ]
    
    for status_data in statuses:
        obj, created = RequestStatus.objects.get_or_create(
            code=status_data['code'],
            defaults={'name': status_data['name']}
        )
        if created:
            created_count += 1
            print(f"Создан статус: {status_data['name']} (code: {status_data['code']})")
        else:
            print(f"Статус уже существует: {status_data['name']}")

    print("Инициализация завершена!")