from django.core.mail import EmailMessage

class EmailService:
    """Сервис для отправки email"""
    
    @staticmethod
    def send_order_notification(request_obj, file_path):
        """Отправка уведомления о новом заказе"""
        email = EmailMessage(
            subject=f"Новая заявка {request_obj.code}",
            body=f"Поступила новая заявка от {request_obj.client.company_name}",
            to=["rassvet-info-vlg@mail.ru"]
        )
        
        email.attach_file(file_path)
        email.send(fail_silently=False)