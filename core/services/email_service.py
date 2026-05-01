from django.conf import settings
from django.core.mail import EmailMessage


class EmailService:
    @staticmethod
    def send_order_notification(request_obj, waybill_url):
        """Отправляет email с ссылкой на Cloudinary"""
        
        items_list = ""
        for item in request_obj.items.all():
            items_list += f"\n- {item.product.name}: {item.quantity} шт. x {item.price} руб. = {item.price * item.quantity} руб."
        
        email = EmailMessage(
            subject=f"Новая заявка {request_obj.code}",
            body=f"""
            Поступила новая заявка от {request_obj.client.company_name}
            Детали заявки:
            - Номер заявки: {request_obj.code}
            - Компания: {request_obj.client.company_name}
            - ИНН: {request_obj.client.tin}
            - Телефон: {request_obj.contact.phone}
            - Email: {request_obj.contact.email}

            Состав заявки:{items_list}

            Накладная доступна по ссылке: {waybill_url}

            ---
            Это автоматическое сообщение, пожалуйста, не отвечайте на него.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=["rassvet-info-vlg@mail.ru"]
        )
        
        # Отправляем письмо
        email.send(fail_silently=False)