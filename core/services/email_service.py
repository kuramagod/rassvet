import os

from django.conf import settings
from django.core.mail import EmailMessage

class EmailService:
    @staticmethod
    def send_order_notification(request_obj, file_path):        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден по пути: {file_path}")

        email = EmailMessage(
            subject=f"Новая заявка {request_obj.code}",
            body=f"Поступила новая заявка от {request_obj.client.company_name}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=["rassvet-info-vlg@mail.ru"]
        )
        
        email.attach_file(file_path.strip())
        
        email.send(fail_silently=True)