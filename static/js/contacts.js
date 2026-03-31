document.addEventListener('DOMContentLoaded', async function () {
    const form = document.getElementById('feedback');
    const contactInput = form.querySelector('input[name="contact"]');

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

        // const response = await fetch(`/api/contact/`, {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json',
        //     },
        //     body: JSON.stringify(data)
        // });

        // if (response.ok) {
        //     window.location.reload();
        // } else {
        //     console.log(response);
        // }

        console.log("Сообщение отправлено!");
    });
});