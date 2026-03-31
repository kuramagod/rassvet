function toggleMobileMenu() {
	const menu = document.getElementById('mobile-menu');
	if (menu) {
		menu.classList.toggle('open');
	}
}

document.addEventListener('click', function(event) {
    const menu = document.getElementById('mobile-menu');
    const menuButton = document.getElementById('menu-button');
    if (menu && menuButton && !menu.contains(event.target) && !menuButton.contains(event.target)) {
        menu.classList.remove('open');
    }
});