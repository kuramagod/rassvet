import io
import tempfile
from datetime import datetime
from django.conf import settings
from docx import Document
from docxtpl import DocxTemplate
import cloudinary
import cloudinary.uploader


cloudinary.config(
    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)

def generate_waybill(request_obj):
    """Генерирует накладную и загружает в Cloudinary"""
    
    template_path = settings.BASE_DIR / "templates" / "docs" / "template.docx"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Шаблон не найден: {template_path}")
    
    doc = DocxTemplate(str(template_path))
    
    now = datetime.now()
    months = [
        "января","февраля","марта","апреля","мая","июня",
        "июля","августа","сентября","октября","ноября","декабря"
    ]
    
    items = []
    total_sum = 0
    
    for item in request_obj.items.all():
        item_sum = item.price * item.quantity
        total_sum += item_sum
        items.append({
            "name": item.product.name,
            "quantity": item.quantity,
            "price": f"{item.price:.2f}",
            "sum": f"{item_sum:.2f}",
        })
    
    context = {
        "day": now.strftime("%d"),
        "mouth": months[now.month - 1],
        "year": now.strftime("%y"),
        "number": request_obj.id,
        "company": request_obj.client.company_name,
        "tin": request_obj.client.tin,
        "items": items,
        "total_sum": f"{total_sum:.2f}",
    }
    
    # Используем временный файл в системной temp папке
    with tempfile.NamedTemporaryFile(mode='w+b', suffix='.docx', delete=False) as tmp_render:
        doc.render(context)
        doc.save(tmp_render.name)
        tmp_render_path = tmp_render.name
    
    tmp_final_path = None
    
    try:
        # Загружаем документ для очистки
        temp_doc = Document(tmp_render_path)
        
        # Очищаем от тегов
        for table in temp_doc.tables:
            rows_to_delete = []
            for i, row in enumerate(table.rows):
                row_text = ' '.join(cell.text for cell in row.cells)
                
                if '{% for' in row_text or '{% endfor' in row_text:
                    rows_to_delete.append(i)
                if row_text.strip() in ['', '-', '|', '+---', '{% for item in items %}', '{% endfor %}']:
                    rows_to_delete.append(i)
            
            for i in sorted(rows_to_delete, reverse=True):
                table._element.remove(table.rows[i]._element)
        
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.docx', delete=False) as tmp_final:
            temp_doc.save(tmp_final.name)
            tmp_final_path = tmp_final.name
        
        upload_result = cloudinary.uploader.upload(
            tmp_final_path,
            resource_type="raw",
            public_id=f"nakladnaya_{request_obj.id}",
            folder="invoices",
            overwrite=True,
        )
        
        request_obj.waybill_url = upload_result["secure_url"]
        request_obj.save(update_fields=["waybill_url"])

        return upload_result["secure_url"]
        
    finally:
        import os
        if os.path.exists(tmp_render_path):
            os.remove(tmp_render_path)
        if os.path.exists(tmp_final_path):
            os.remove(tmp_final_path)