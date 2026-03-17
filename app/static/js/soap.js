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
