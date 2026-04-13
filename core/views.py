import os
import json

from django.http import FileResponse, Http404, JsonResponse
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, TemplateView, View
from django.core.exceptions import ValidationError

from .models import Category, DeliveryType, Message, News, Product, Request
from .services.order_service import OrderService
from .services.file_service import WaybillService
from .services.email_service import EmailService


def home_page(request):
    products = Product.objects.filter(is_active=True)[:3]   
    news = News.objects.all() 
    return render(request, "core/index.html", {"products": products, "news": news})


class CatalogView(TemplateView):
    template_name = "core/catalog.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(is_active=True)
        context['categories'] = Category.objects.all()
        return context


class ProductPage(DetailView):
    model = Product
    template_name = "core/product.html"
    slug_url_kwarg = "product_slug"
    context_object_name = "product"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related(
            'characteristics', 
            'images' 
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['characteristics'] = self.object.characteristics.all()
        context['product_images'] = self.object.images.all()
        return context


def about_page(request):
    return render(request, "core/about.html")


def contact_page(request):
    return render(request, "core/contact.html")


@require_POST
def contact_message(request):
    try:
        data = json.loads(request.body)
        Message.objects.create(
            name=data.get("username"),
            email=data.get("contact") if "@" in data.get("contact", "") else "",
            phone=data.get("contact") if "@" not in data.get("contact", "") else "",
            text=data.get("message")
        )
        return JsonResponse({'success': True}, status=201)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


class OrderView(TemplateView):
    template_name = "core/order.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delivery_types'] = DeliveryType.objects.all()
        context['products'] = Product.objects.filter(is_active=True)
        return context


@method_decorator(csrf_exempt, name='dispatch')
class CreateOrderView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            order_service = OrderService()
            
            request_obj = order_service.create_order(data)
            
            try:
                file_path = WaybillService.get_or_generate_waybill(request_obj)
                EmailService.send_order_notification(request_obj, file_path)
            except Exception as e:
                print(f"Error generating waybill or sending email: {e}")
            
            return JsonResponse({
                'success': True,
                'order_number': request_obj.code,
                'request_id': request_obj.id,
                'download_url': f'/api/download-waybill/{request_obj.id}/',
                'message': f'Заявка #{request_obj.code} успешно создана'
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Неверный формат данных'}, status=400)
            
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


class DownloadWaybillView(View):
    def get(self, request, request_id, *args, **kwargs):
        try:
            try:
                request_obj = Request.objects.get(id=request_id)
            except Request.DoesNotExist:
                raise Http404("Заявка не найдена")
            
            file_path = WaybillService.get_or_generate_waybill(request_obj)
            
            response = FileResponse(
                open(file_path, 'rb'),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                as_attachment=True,
                filename=f'Накладная_{request_obj.code}_{request_id}.docx'
            )
            
            response['Content-Length'] = os.path.getsize(file_path)
            return response
            
        except FileNotFoundError as e:
            raise Http404(str(e))
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Ошибка при скачивании файла: {str(e)}'}, status=500)