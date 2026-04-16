from docx import Document
from docx.shared import Pt
import os
from datetime import datetime
from docxtpl import DocxTemplate
from django.conf import settings

def generate_waybill(request_obj):
    template_path = os.path.join(
        settings.BASE_DIR,
        "templates",
        "docs",
        "template.docx"
    )

    output_dir = os.path.join(settings.MEDIA_ROOT, "invoices")
    os.makedirs(output_dir, exist_ok=True)

    # Сначала рендерим через docxtpl во временный файл
    doc = DocxTemplate(template_path)

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

    # Рендерим во временный файл
    temp_path = os.path.join(output_dir, f"temp_{request_obj.id}.docx")
    doc.render(context)
    doc.save(temp_path)
    
    final_doc = Document(temp_path)
    
    # Проходим по всем таблицам
    for table in final_doc.tables:
        rows_to_delete = []
        
        for i, row in enumerate(table.rows):
            row_text = ' '.join(cell.text for cell in row.cells)
            
            # Если в строке есть теги циклов - помечаем на удаление
            if '{% for' in row_text or '{% endfor' in row_text:
                rows_to_delete.append(i)
            # Также удаляем пустые строки с дефисами
            if row_text.strip() in ['', '-', '|', '+---', '{% for item in items %}', '{% endfor %}']:
                rows_to_delete.append(i)
        
        # Удаляем помеченные строки (с конца, чтобы не сбивать индексы)
        for i in sorted(rows_to_delete, reverse=True):
            table._element.remove(table.rows[i]._element)
    
    # Сохраняем финальный документ
    final_path = os.path.join(output_dir, f"nakladnaya_{request_obj.id}.docx")
    final_doc.save(final_path)
    
    # Удаляем временный файл
    os.remove(temp_path)
    
    return f"/media/invoices/nakladnaya_{request_obj.id}.docx"