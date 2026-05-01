import requests
from django.conf import settings

class EmailService:
    @staticmethod
    def send_order_notification(request_obj, waybill_url):
        items_list = ""
        for item in request_obj.items.all():
            items_list += f"\n- {item.product.name}: {item.quantity} шт. x {item.price} руб. = {item.price * item.quantity} руб."

        body = f"""
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
        """

        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": "onboarding@resend.dev",
                "to": ["rassvet-info-vlg@mail.ru"],
                "subject": f"Заявка {request_obj.code}",
                "text": body,
            },
            timeout=10
        )

        if response.status_code >= 400:
            raise Exception(response.text)