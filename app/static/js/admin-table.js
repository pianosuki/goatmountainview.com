/**
 * Admin Table - Scroll Position & AJAX Delete
 * Handles scroll position preservation and AJAX delete operations
 */

// Restore scroll position when returning from edit page
window.addEventListener('pageshow', function(event) {
    const scrollPos = sessionStorage.getItem('adminScrollPosition');
    if (scrollPos) {
        setTimeout(() => {
            window.scrollTo(0, parseInt(scrollPos));
            sessionStorage.removeItem('adminScrollPosition');
        }, 100);
    }
});

/**
 * Delete a row via AJAX
 * @param {string|number} rowId - The ID of the row to delete
 * @param {string} tableName - The name of the table
 */
async function deleteRow(rowId, tableName) {
    if (!confirm('Are you sure you want to delete this?')) {
        return;
    }
    
    const rowElement = document.getElementById(`row-${rowId}`);
    if (!rowElement) return;
    
    // Show loading state
    rowElement.style.opacity = '0.5';
    
    try {
        const response = await fetch(`/api/admin/${tableName}/${rowId}`, {
            method: 'DELETE',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Animate row removal
            rowElement.style.transition = 'all 0.3s ease';
            rowElement.style.transform = 'translateX(100%)';
            rowElement.style.opacity = '0';
            
            setTimeout(() => {
                rowElement.remove();
                // Update count
                const cardHeader = document.querySelector('.card-header');
                if (cardHeader) {
                    const currentText = cardHeader.textContent;
                    const match = currentText.match(/Records \((\d+)/);
                    if (match) {
                        const newCount = parseInt(match[1]) - 1;
                        cardHeader.textContent = currentText.replace(match[0], `Records (${newCount}`);
                    }
                }
            }, 300);
        } else {
            alert('Error: ' + result.error);
            rowElement.style.opacity = '1';
        }
    } catch (error) {
        alert('Error deleting row: ' + error.message);
        rowElement.style.opacity = '1';
    }
}
