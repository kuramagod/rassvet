// Функция фильтрации
function filterProducts(category) {
	const products = document.querySelectorAll('.product-card');
	let visibleCount = 0;

	products.forEach(product => {
        const productCategory = product.getAttribute('data-category');
            if (category === 'All' || productCategory === category) {
                product.style.display = 'block';
                visibleCount++;
            } else {
                product.style.display = 'none';
            }
	});
  
	const noProducts = document.getElementById('no-products');
    if (visibleCount === 0) {
        noProducts.classList.remove('hidden');
    } else {
        noProducts.classList.add('hidden');
    }

	// Обновление активной кнопки
	document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('bg-primary', 'text-white', 'shadow-md');
        btn.classList.add('bg-gray-100', 'text-gray-700');
	});

	event.target.classList.add('bg-primary', 'text-white', 'shadow-md');
	event.target.classList.remove('bg-gray-100', 'text-gray-700');
}
