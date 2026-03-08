// Smooth animation for Nordiska logo on scroll
document.addEventListener('DOMContentLoaded', function() {
    const logoImg = document.querySelector('.nordiska-logo-container img');

    if (logoImg) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    setTimeout(function() {
                        logoImg.classList.add('loaded');
                    }, 200);
                    observer.unobserve(logoImg);
                }
            });
        }, {
            threshold: 0.3,
            rootMargin: '0px'
        });

        observer.observe(logoImg);
    }
});

// Lightbox functions
function openLightbox(imageSrc, caption) {
    const lightbox = document.getElementById('nordiska-lightbox');
    const lightboxImg = document.getElementById('nordiska-lightbox-img');
    const lightboxCaption = document.getElementById('nordiska-lightbox-caption');

    lightboxImg.src = imageSrc;
    lightboxCaption.textContent = caption;
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeLightbox(event) {
    if (event.target === event.currentTarget) {
        const lightbox = document.getElementById('nordiska-lightbox');
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function closeLightboxBtn() {
    const lightbox = document.getElementById('nordiska-lightbox');
    lightbox.classList.remove('active');
    document.body.style.overflow = '';
}

// Close on Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const lightbox = document.getElementById('nordiska-lightbox');
        if (lightbox.classList.contains('active')) {
            closeLightboxBtn();
        }
    }
});
