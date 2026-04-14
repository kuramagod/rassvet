from docxtpl import DocxTemplate
import os
from datetime import datetime
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

    doc.render(context)

    document = doc.docx

    for table in document.tables:
        rows_to_delete = []

        for i, row in enumerate(table.rows):
            row_text = " ".join(cell.text for cell in row.cells)

            if "{% for" in row_text or "{% endfor" in row_text:
                rows_to_delete.append(i)

        for i in sorted(rows_to_delete, reverse=True):
            table._element.remove(table.rows[i]._element)

    final_path = os.path.join(output_dir, f"nakladnaya_{request_obj.id}.docx")

    document.save(final_path)

    return f"/media/invoices/nakladnaya_{request_obj.id}.docx"