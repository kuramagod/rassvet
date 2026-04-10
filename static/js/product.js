document.addEventListener('DOMContentLoaded', () => {
    const track = document.getElementById('slider-track');
    const dots = document.querySelectorAll('.slider-dot');
    
    if (!track) return;

    const slidesCount = parseInt(track.getAttribute('data-slides-count')) || 1;
    let currentIndex = 0;


    const updateSlider = () => {
        track.style.transform = `translateX(-${currentIndex * 100}%)`;
        
        dots.forEach((dot, index) => {
            if (index === currentIndex) {
                dot.classList.add('bg-white');
                dot.classList.remove('bg-white/50');
            } else {
                dot.classList.remove('bg-white');
                dot.classList.add('bg-white/50');
            }
        });
    };

    window.nextSlide = () => {
        currentIndex = (currentIndex + 1) % slidesCount;
        updateSlider();
    };

    window.prevSlide = () => {
        currentIndex = (currentIndex - 1 + slidesCount) % slidesCount;
        updateSlider();
    };

    window.goToSlide = (index) => {
        currentIndex = index;
        updateSlider();
    };

    if (dots.length > 0) {
        updateSlider();
    }
});