document.addEventListener('DOMContentLoaded', async function () {
    const form = document.getElementById('feedback');
    const contactInput = form.querySelector('input[name="contact"]');
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Очищаем ошибку при вводе
    contactInput.addEventListener('input', () => {
        contactInput.setCustomValidity('');
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        var contact = data.contact;

        // Валидируем контакт
        if (/^\d+$/.test(contact)) {
            if (!/^(7|8)\d{10}$/.test(contact)) {
                contactInput.setCustomValidity('Некорректный формат номера. Введите номер по Российскому стандарту.');
                contactInput.reportValidity();
                return;
            }
        } else {
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contact)) {
                contactInput.setCustomValidity('Некорректный формат email адреса');
                contactInput.reportValidity();
                return;
            }
        }

        const response = await fetch(`/api/create_message/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(data)
        });

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        if (response.ok) {
            form.reset();
            showSuccessMessage("Сообщение успешно отправлено");
        } else {
            showErrorMessage("Ошибка при отправке сообщения. Пожалуйста, попробуйте позже.");
        }
    });
});


// Функция для показа сообщения об успехе
function showSuccessMessage(successMessage) {
    let successDiv = document.getElementById('submit-success');
    if (!successDiv) {
        successDiv = document.createElement('div');
        successDiv.id = 'submit-success';
        successDiv.className = 'fixed bottom-4 left-1/2 transform -translate-x-1/2 z-50 max-w-md';
        document.body.appendChild(successDiv);
    }
    
    successDiv.innerHTML = `
        <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded-lg shadow-lg fade-in">
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                </div>
                <div class="ml-3">
                    <p class="text-sm text-green-700">${successMessage}</p>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-auto pl-3">
                    <svg class="h-5 w-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        </div>
    `;
    
    // Автоматически удаляем сообщение через 5 секунд
    setTimeout(() => {
        if (successDiv && successDiv.parentElement) {
            successDiv.remove();
        }
    }, 5000);
}

// Функция для показа сообщения об ошибке
function showErrorMessage(errorMessage) {
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