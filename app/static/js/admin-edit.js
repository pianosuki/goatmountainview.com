/**
 * Admin Edit - Scroll Position Preservation
 * Saves scroll position when navigating to edit page
 */

// Save scroll position before navigating to edit page
sessionStorage.setItem('adminScrollPosition', window.scrollY);

// Restore scroll position when returning from edit
window.addEventListener('pageshow', function(event) {
    const scrollPos = sessionStorage.getItem('adminScrollPosition');
    if (scrollPos) {
        setTimeout(() => {
            window.scrollTo(0, parseInt(scrollPos));
        }, 100);
    }
});
