function getCSRFToken() {
    // Пытаемся получить из cookie
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken=')) {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                break;
            }
        }
    }
    // Если не нашли в cookie, пробуем из мета-тега
    if (!cookieValue) {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            cookieValue = metaTag.getAttribute('content');
        }
    }
    return cookieValue;
}

// Используем продукты из глобальной переменной
const products = window.availableProducts || [];

let currentStep = 1;
const totalSteps = 5;

document.addEventListener('DOMContentLoaded', () => {
    initDeliveryToggle();
    updateButtons();
    updateProgress();
    
    // Инициализируем первый товар, если список пуст
    const itemsContainer = document.getElementById('order-items');
    if (itemsContainer && itemsContainer.children.length === 0) {
        addOrderItem();
    }
});

// Навигация по шагам
window.nextStep = function() {
    if (currentStep < totalSteps) {
        if (!validateCurrentStep()) 
			return;

        if (currentStep === 4) {
            updateReview();
        }

        document.getElementById(`step-${currentStep}`).style.display = 'none';
        currentStep++;
        document.getElementById(`step-${currentStep}`).style.display = 'block';
        
        updateProgress();
        updateButtons();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
        // Финальная отправка на 5-м шаге
        submitOrder();
    }
};

window.prevStep = function() {
    if (currentStep > 1) {
        document.getElementById(`step-${currentStep}`).style.display = 'none';
        currentStep--;
        document.getElementById(`step-${currentStep}`).style.display = 'block';
        
        updateProgress();
        updateButtons();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
};

function emptyProductError(bool) {
    errorBlock = document.getElementById('errorValidProduct');
    
    if (bool == true) {
        errorBlock.innerHTML = `
            <div class="bg-red-50 p-4 rounded-lg flex items-start gap-3 text-sm text-red-800" id="errorValidProduct">
                <svg class="h-5 w-5 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p>Выберите хотя бы один товар.</p>
            </div>  
        `;
    } else {
        errorBlock.innerHTML = ``;
    }
}

// Управление списком товаров
window.addOrderItem = function() {
    const emptyItems = document.getElementById('empty-items');
    if (emptyItems) emptyItems.style.display = 'none';

    const itemsContainer = document.getElementById('order-items');
    const itemDiv = document.createElement('div');
    
    itemDiv.className = 'order-item flex flex-col md:flex-row gap-4 p-4 bg-gray-50 rounded-xl border border-gray-100 items-end md:items-center mb-4 fade-in';
    itemDiv.innerHTML = `
        <div class="flex-grow w-full">
            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Товар</label>
            <select class="product-select w-full border-gray-300 rounded-lg p-2.5 border outline-none focus:ring-rassvet-orange focus:border-rassvet-orange">
                ${products.map(p => `<option value="${p.id}">${p.name}</option>`).join('')}
            </select>
        </div>
        <div class="w-full md:w-48">
            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Объем (тонн)</label>
            <input type="number" min="1" value="20" class="quantity-input w-full border-gray-300 rounded-lg p-2.5 border outline-none focus:ring-rassvet-orange focus:border-rassvet-orange" />
        </div>
        <button type="button" onclick="removeOrderItem(this)" class="text-red-500 hover:bg-red-50 p-2.5 rounded-lg transition-colors" title="Удалить">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
        </button>
    `;
    
    emptyProductError(false);
    itemsContainer.appendChild(itemDiv);
};

window.removeOrderItem = function(button) {
    button.closest('.order-item').remove();
    const itemsContainer = document.getElementById('order-items');
    if (itemsContainer.children.length === 0) {
        document.getElementById('empty-items').style.display = 'block';
    }
};

//Валидация и вспомогательные функции
function raiseErrorValidation(input, message) {
    input.setCustomValidity(message);
    input.reportValidity();
}

function validateCurrentStep() {
    if (currentStep === 1) {
        const company = document.getElementById('companyName');
        const inn = document.getElementById('inn');
        const address = document.getElementById('address');
        if (!company.value.trim()) {
            raiseErrorValidation(company, 'Введите наименование вашей компании')
            return;
        } else if (!inn.value.trim()) {
            raiseErrorValidation(inn, 'Введите ИНН вашей компании')
            return;
        } else if (!address.value.trim()) {
            raiseErrorValidation(address, 'Введите адрес вашей компании')
            return;
        };

        // Валидация ИНН
        if (!/^\d+$/.test(inn.value.trim())) {
            raiseErrorValidation(inn, 'ИНН должен состоят только из цифр')
            return;
        };

    } 
    else if (currentStep === 2) {
        const name = document.getElementById('contactPerson');
        const phone = document.getElementById('phone');
        const email = document.getElementById('email');
        if (!name.value.trim()) {
            raiseErrorValidation(name, 'Введите ваше ФИО')
            return;
        } else if (!phone.value.trim()) {
            raiseErrorValidation(phone, 'Введите ваш номер телефона')
            return;
        } else if (!email.value.trim()) {
            raiseErrorValidation(email, 'Введите ваш адрес электронной почты')
            return;
        };

        // Валидация номера
        if (!/^(\+?7|8)\d{10}$/.test(phone.value.trim())) {
            raiseErrorValidation(phone, 'Некорректный формат номера. Введите номер по Российскому стандарту.')
            return;
        };
        // Валидация почты 
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
            raiseErrorValidation(email, 'Некорректный формат email адреса')
            return;
        }
    } 
    else if (currentStep === 3) {
        if (document.querySelectorAll('.order-item').length === 0) {
            emptyProductError(true);
            return;
        }
    }
    else if (currentStep === 5) {
        if (!document.getElementById('confirm-checkbox').checked) {
            document.getElementById('confirm').className = 'flex items-start gap-3 p-4 border border-gray-200 rounded-lg bg-red-100';
            return;
        }
    }
    return true;
}

function updateProgress() {
    const bar = document.getElementById('progress-bar');
    const indicator = document.getElementById('step-indicator');
    if (bar) bar.style.width = `${(currentStep / totalSteps) * 100}%`;
    if (indicator) indicator.textContent = `Шаг ${currentStep} из ${totalSteps}`;
}

function updateButtons() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    
    prevBtn.classList.toggle('invisible', currentStep === 1);
    
    if (currentStep === totalSteps) {
        nextBtn.textContent = 'Отправить заявку';
        nextBtn.classList.remove('bg-rassvet-green', 'hover:bg-green-800');
        nextBtn.classList.add('bg-rassvet-orange', 'hover:bg-orange-600');
    } else {
        nextBtn.innerHTML = 'Далее <svg class="ml-2 h-3 w-3 sm:h-4 sm:w-4 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>';
        nextBtn.classList.remove('bg-rassvet-orange', 'hover:bg-orange-600');
        nextBtn.classList.add('bg-rassvet-green', 'hover:bg-green-800');
    }
}

function initDeliveryToggle() {
    const options = document.querySelectorAll('.delivery-option');
    options.forEach(opt => {
        opt.addEventListener('click', function() {
            const radio = this.querySelector('input[type="radio"]');
            radio.checked = true;
            
            options.forEach(o => o.classList.remove('border-rassvet-orange', 'bg-orange-50', 'ring-1', 'ring-rassvet-orange'));
            this.classList.add('border-rassvet-orange', 'bg-orange-50', 'ring-1', 'ring-rassvet-orange');
            
            // Получаем ID типа доставки
            const deliveryTypeId = radio.value;
            const deliveryTypeName = getDeliveryTypeName(deliveryTypeId);
            
            // Показываем поле адреса только для доставки (не для самовывоза)
            const isPickup = deliveryTypeName === 'Самовывоз';
            document.getElementById('delivery-address-block').style.display = isPickup ? 'none' : 'block';
        });
    });
}

// Функция для получения названия типа доставки по ID
function getDeliveryTypeName(id) {
    const deliveryType = window.deliveryTypes.find(dt => dt.id == id);
    return deliveryType ? deliveryType.name : '-';
}

// Сводка данных перед отправкой (Шаг 5)
function updateReview() {
    document.getElementById('review-company').textContent = document.getElementById('companyName').value;
    document.getElementById('review-inn').textContent = document.getElementById('inn').value;
    document.getElementById('review-contact').textContent = document.getElementById('contactPerson').value;
    document.getElementById('review-phone').textContent = document.getElementById('phone').value;
    document.getElementById('review-email').textContent = document.getElementById('email').value;
    
    const reviewItems = document.getElementById('review-items');
    reviewItems.innerHTML = '';
    
    document.querySelectorAll('.order-item').forEach(item => {
        const select = item.querySelector('.product-select');
        const qty = item.querySelector('.quantity-input').value;
        const name = select.options[select.selectedIndex].text;
        
        const li = document.createElement('div');
        li.className = 'flex justify-between text-sm border-b border-gray-100 pb-1';
        li.innerHTML = `<span>${name}</span><span class="font-bold">${qty} т.</span>`;
        reviewItems.appendChild(li);
    });

    // Получаем выбранный тип доставки
    const selectedRadio = document.querySelector('input[name="deliveryType"]:checked');
    if (selectedRadio) {
        const deliveryTypeId = selectedRadio.value;
        const deliveryTypeName = getDeliveryTypeName(deliveryTypeId);
        document.getElementById('review-delivery').textContent = deliveryTypeName;
        
        // Показываем адрес только если это не самовывоз
        const isPickup = deliveryTypeName === 'Самовывоз';
        const addr = document.getElementById('deliveryAddress').value;
        const reviewAddr = document.getElementById('review-address');
        reviewAddr.textContent = (!isPickup && addr) ? addr : '';
    } else {
        document.getElementById('review-delivery').textContent = '-';
    }
}

// Отправка формы на сервер
window.submitOrder = function() {
    if (!validateCurrentStep()) return;
    
    // Собираем данные для отправки
    const orderData = {
        // Шаг 1: Информация о компании
        company_name: document.getElementById('companyName').value.trim(),
        inn: document.getElementById('inn').value.trim(),
        address: document.getElementById('address').value.trim(),
        
        // Шаг 2: Контактная информация
        contact_person: document.getElementById('contactPerson').value.trim(),
        position: document.getElementById('position').value.trim() || '',
        phone: document.getElementById('phone').value.trim(),
        email: document.getElementById('email').value.trim(),
        
        // Шаг 4: Доставка и комментарии
        delivery_type: document.querySelector('input[name="deliveryType"]:checked').value,
        delivery_address: document.getElementById('deliveryAddress').value.trim(),
        comments: document.getElementById('comments').value.trim(),
        
        // Шаг 3: Товары
        items: []
    };
    
    // Собираем товары
    document.querySelectorAll('.order-item').forEach(item => {
        const select = item.querySelector('.product-select');
        const qty = item.querySelector('.quantity-input').value;
        const productId = select.value;
        const productName = select.options[select.selectedIndex].text;
        
        orderData.items.push({
            product_id: productId,
            product_name: productName,
            quantity: parseInt(qty)
        });
    });
    
    // Проверяем, что товары есть
    if (orderData.items.length === 0) {
        emptyProductError(true);
        return;
    }
    
    // Отключаем кнопку отправки
    const nextBtn = document.getElementById('next-btn');
    const originalText = nextBtn.innerHTML;
    nextBtn.disabled = true;
    nextBtn.innerHTML = 'Отправка...';
    
    // Получаем CSRF токен
    const csrftoken = getCSRFToken();
    
    // Отправляем данные на сервер
    fetch('/api/create_request/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(orderData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.order_number);
        } else {
            showErrorMessage(data.error || 'Произошла ошибка при отправке заявки');
            nextBtn.disabled = false;
            nextBtn.innerHTML = originalText;
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showErrorMessage('Произошла ошибка при отправке заявки. Пожалуйста, проверьте подключение к интернету и попробуйте снова.');
        nextBtn.disabled = false;
        nextBtn.innerHTML = originalText;
    });
};

// Функция для показа сообщения об успехе
function showSuccessMessage(orderNumber) {
    const wizard = document.getElementById('order-wizard');
    
    wizard.innerHTML = `
        <div class="p-12 text-center fade-in">
            <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg class="h-10 w-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
            </div>
            <h2 class="text-3xl font-bold text-gray-900 mb-4">Заявка #${orderNumber} принята!</h2>
            <p class="text-gray-600 mb-8 text-lg">
                Наш менеджер свяжется с вами в ближайшее время для уточнения деталей и формирования счета.
            </p>
            <div class="flex justify-center gap-4">
                <a href="/" class="bg-rassvet-green text-white px-6 py-3 rounded-lg font-bold hover:bg-green-800 transition">На главную</a>
                <button onclick="window.print()" class="border border-gray-300 px-6 py-3 rounded-lg font-bold hover:bg-gray-50 transition">Печать заявки</button>
            </div>
        </div>
    `;
}

// Функция для показа сообщения об ошибке
function showErrorMessage(errorMessage) {
    // Создаем или обновляем блок с ошибкой
    let errorDiv = document.getElementById('submit-error');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.id = 'submit-error';
        errorDiv.className = 'fixed bottom-4 left-1/2 transform -translate-x-1/2 z-50 max-w-md';
        document.body.appendChild(errorDiv);
    }
    
    errorDiv.innerHTML = `
        <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg shadow-lg fade-in">
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                </div>
                <div class="ml-3">
                    <p class="text-sm text-red-700">${errorMessage}</p>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-auto pl-3">
                    <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        </div>
    `;
    
    // Автоматически удаляем сообщение через 5 секунд
    setTimeout(() => {
        if (errorDiv && errorDiv.parentElement) {
            errorDiv.remove();
        }
    }, 5000);
}