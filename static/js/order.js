// Временные константы
const products = [
    { id: '1', name: 'Пшеница озимая (3 класс)' },
    { id: '2', name: 'Ячмень фуражный' },
    { id: '3', name: 'Кукуруза зерновая' },
    { id: '4', name: 'Масло подсолнечное нерафинированное' },
    { id: '5', name: 'Семена подсолнечника масличного' }
];

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
            
            document.getElementById('delivery-address-block').style.display = 
                radio.value === 'pickup' ? 'none' : 'block';
        });
    });
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

    const delType = document.querySelector('input[name="deliveryType"]:checked').value;
    document.getElementById('review-delivery').textContent = delType === 'delivery' ? 'Доставка поставщиком' : 'Самовывоз';
    
    const addr = document.getElementById('deliveryAddress').value;
    const reviewAddr = document.getElementById('review-address');
    reviewAddr.textContent = (delType === 'delivery' && addr) ? addr : '';
}

// Имитация отправки формы
window.submitOrder = function() {
    if (!validateCurrentStep()) return;

    const wizard = document.getElementById('order-wizard');
    const orderNum = Math.floor(1000 + Math.random() * 9000);
    
    wizard.innerHTML = `
        <div class="p-12 text-center fade-in">
            <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg class="h-10 w-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
            </div>
            <h2 class="text-3xl font-bold text-gray-900 mb-4">Заявка #REQ-${orderNum} принята!</h2>
            <p class="text-gray-600 mb-8 text-lg">
                Наш менеджер свяжется с вами в ближайшее время для уточнения деталей и формирования счета.
            </p>
            <div class="flex justify-center gap-4">
                <a href="/" class="bg-rassvet-green text-white px-6 py-3 rounded-lg font-bold hover:bg-green-800 transition">На главную</a>
                <button onclick="window.print()" class="border border-gray-300 px-6 py-3 rounded-lg font-bold hover:bg-gray-50 transition">Печать заявки</button>
            </div>
        </div>
    `;
};