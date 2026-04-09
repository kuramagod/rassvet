import os
from django.conf import settings
from ..utils import generate_waybill

class WaybillService:
    """Сервис для работы с накладными"""
    
    @staticmethod
    def get_file_path(request_id):
        """Получить путь к файлу накладной"""
        return os.path.join(
            settings.MEDIA_ROOT, 
            "invoices", 
            f"nakladnaya_{request_id}.docx"
        )
    
    @classmethod
    def get_or_generate_waybill(cls, request_obj):
        """Получить существующую накладную или сгенерировать новую"""
        file_path = cls.get_file_path(request_obj.id)
        
        if not os.path.exists(file_path):
            generate_waybill(request_obj)
            
        if not os.path.exists(file_path):
            raise FileNotFoundError("Файл накладной не найден")
            
        return file_path