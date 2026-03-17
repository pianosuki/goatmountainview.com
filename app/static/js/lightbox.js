document.addEventListener('DOMContentLoaded', function() {
    const lightbox = document.getElementById('lightbox');
    if (!lightbox) {
        return;
    }

    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxCaption = document.getElementById('lightbox-caption');
    const closeButton = lightbox.querySelector('[data-lightbox-close]');

    function openLightbox(imageSrc, caption) {
        if (!imageSrc || !lightboxImg) {
            return;
        }

        lightboxImg.src = imageSrc;
        lightboxImg.alt = caption || 'Expanded artwork';

        if (lightboxCaption) {
            lightboxCaption.textContent = caption || '';
        }

        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }

    const triggers = document.querySelectorAll('[data-lightbox-src]');
    triggers.forEach(function(trigger) {
        trigger.addEventListener('click', function(event) {
            event.preventDefault();
            openLightbox(trigger.dataset.lightboxSrc, trigger.dataset.lightboxCaption);
        });

        if (trigger.tagName !== 'BUTTON') {
            trigger.addEventListener('keydown', function(event) {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    openLightbox(trigger.dataset.lightboxSrc, trigger.dataset.lightboxCaption);
                }
            });
        }
    });

    lightbox.addEventListener('click', function(event) {
        if (event.target === event.currentTarget) {
            closeLightbox();
        }
    });

    if (closeButton) {
        closeButton.addEventListener('click', function(event) {
            event.preventDefault();
            closeLightbox();
        });
    }

    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && lightbox.classList.contains('active')) {
            closeLightbox();
        }
    });
});
