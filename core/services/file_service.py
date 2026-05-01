from ..utils import generate_waybill


class WaybillService:
    """Сервис для работы с накладными в Cloudinary"""
    
    @staticmethod
    def get_waybill_url(request_obj):
        if request_obj.waybill_url:
            return request_obj.waybill_url
        
        waybill_url = generate_waybill(request_obj)
        return waybill_url
    
    @staticmethod
    def get_or_generate_waybill(request_obj):
        return WaybillService.get_waybill_url(request_obj)