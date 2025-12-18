document.addEventListener('DOMContentLoaded', () => {
    const sliderContainer = document.getElementById('info-slider');
    const promoBanner = document.getElementById('promo-banner');
    const closeBtn = promoBanner ? promoBanner.querySelector('.close-btn') : null;
    const mainInfoSection = document.querySelector('.main-info-section'); 

    if (sliderContainer) {
        const slides = sliderContainer.querySelectorAll('.slide');
        const dots = sliderContainer.querySelectorAll('.dot');
        const prevBtn = sliderContainer.querySelector('.prev-btn');
        const nextBtn = sliderContainer.querySelector('.next-btn');

        let currentSlide = 0;
        const totalSlides = slides.length;

        function showSlide(index) {
            if (index >= totalSlides) {
                currentSlide = 0;
            } else if (index < 0) {
                currentSlide = totalSlides - 1;
            } else {
                currentSlide = index;
            }

            slides.forEach((slide, i) => {
                slide.classList.toggle('active-slide', i === currentSlide);
            });

            dots.forEach((dot, i) => {
                dot.classList.toggle('active-dot', i === currentSlide);
            });
        }

        prevBtn.addEventListener('click', () => {
            showSlide(currentSlide - 1);
        });

        nextBtn.addEventListener('click', () => {
            showSlide(currentSlide + 1);
        });

        dots.forEach(dot => {
            dot.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.slide);
                showSlide(index);
            });
        });

        showSlide(currentSlide);
        setInterval(() => {
            showSlide(currentSlide + 1);
        }, 2000); 
    }
    
    const fullListBtn = document.querySelector('.full-list-btn');
    const hideListBtn = document.querySelector('.hide-list-btn');
    const moreServices = document.getElementById('more-services');

    if (fullListBtn && moreServices) {
        fullListBtn.addEventListener('click', (e) => {
            e.preventDefault();
            moreServices.classList.add('show');
            moreServices.setAttribute('aria-hidden', 'false');
            fullListBtn.setAttribute('aria-expanded', 'true');
            if (hideListBtn) hideListBtn.style.display = 'block';
            setTimeout(() => {
                moreServices.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 60);
        });
    }

    if (hideListBtn && moreServices) {
        hideListBtn.addEventListener('click', (e) => {
            e.preventDefault();
            moreServices.classList.remove('show');
            moreServices.setAttribute('aria-hidden', 'true');
            fullListBtn.setAttribute('aria-expanded', 'false');
            hideListBtn.style.display = 'none';
            setTimeout(() => {
                const servicesHeading = document.querySelector('.services-section .section-heading');
                if (servicesHeading) servicesHeading.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 60);
        });
    }
});