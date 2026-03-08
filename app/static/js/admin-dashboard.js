/**
 * Admin Dashboard JavaScript
 * Handles navigation and interactions on the admin dashboard
 */

/**
 * Navigate to a specific admin table page
 * @param {string} table - The table name to navigate to
 */
function navigateTo(table) {
    // Create a temporary form and submit
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/admin';
    
    const actionInput = document.createElement('input');
    actionInput.type = 'hidden';
    actionInput.name = 'action';
    actionInput.value = 'edit';
    
    const tableInput = document.createElement('input');
    tableInput.type = 'hidden';
    tableInput.name = 'table_name';
    tableInput.value = table;
    
    form.appendChild(actionInput);
    form.appendChild(tableInput);
    document.body.appendChild(form);
    form.submit();
}

/**
 * Initialize dashboard on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Dashboard is ready - no additional initialization needed
    // Navigation is handled by navigateTo() function
});
