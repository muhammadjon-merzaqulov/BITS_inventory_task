// Smart Inventory System - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Smart Inventory System Initialized');
    
    // Initialize formset management
    initializeFormset();
    
    // Initialize auto-dismiss alerts
    initializeAlerts();
});

// Formset Management for Invoice Items
function initializeFormset() {
    const addButton = document.getElementById('add-item-btn');
    const formsetContainer = document.getElementById('items-tbody');
    
    if (!addButton || !formsetContainer) {
        return; // Not on invoice form page
    }
    
    // Get the management form
    const totalFormsInput = document.querySelector('input[name$="-TOTAL_FORMS"]');
    
    // Add click event to add button
    addButton.addEventListener('click', function(e) {
        e.preventDefault();
        addFormsetRow();
    });
    
    // Function to add a new row
    function addFormsetRow() {
        const totalForms = parseInt(totalFormsInput.value);
        const newFormIndex = totalForms;
        
        // Clone the first row
        const firstRow = formsetContainer.querySelector('.item-row');
        if (!firstRow) {
            console.error('No item row found to clone');
            return;
        }
        
        const newRow = firstRow.cloneNode(true);
        
        // Update form index in all inputs
        const inputs = newRow.querySelectorAll('input, select');
        inputs.forEach(function(input) {
            // Update name attribute
            if (input.name) {
                input.name = input.name.replace(/-\d+-/, `-${newFormIndex}-`);
            }
            // Update id attribute
            if (input.id) {
                input.id = input.id.replace(/-\d+-/, `-${newFormIndex}-`);
            }
            // Clear value for new row
            if (input.type !== 'checkbox' && input.type !== 'hidden') {
                input.value = '';
            }
            if (input.type === 'checkbox' && input.name.includes('DELETE')) {
                input.checked = false;
            }
        });
        
        // Clear the subtotal field
        const subtotalField = newRow.querySelector('.item-subtotal');
        if (subtotalField) {
            subtotalField.value = '0.00';
        }
        
        // Add event listeners to new inputs
        const quantityInput = newRow.querySelector('.item-quantity');
        const priceInput = newRow.querySelector('.item-price');
        if (quantityInput) {
            quantityInput.addEventListener('input', calculateTotals);
        }
        if (priceInput) {
            priceInput.addEventListener('input', calculateTotals);
        }
        
        // Append the new row
        formsetContainer.appendChild(newRow);
        
        // Update total forms count
        totalFormsInput.value = newFormIndex + 1;
        
        console.log(`Added new formset row. Total forms: ${totalFormsInput.value}`);
    }
    
    // Add event listeners for existing rows
    document.querySelectorAll('.item-quantity, .item-price').forEach(function(input) {
        input.addEventListener('input', calculateTotals);
    });
    
    // Add event listener for delete checkboxes
    document.querySelectorAll('input[type="checkbox"][name$="-DELETE"]').forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            const row = this.closest('.item-row');
            if (this.checked) {
                row.style.opacity = '0.5';
                row.style.textDecoration = 'line-through';
            } else {
                row.style.opacity = '1';
                row.style.textDecoration = 'none';
            }
            calculateTotals();
        });
    });
    
    // Add event listener for discount field
    const discountField = document.querySelector('input[name="discount"]');
    if (discountField) {
        discountField.addEventListener('input', calculateTotals);
    }
}

// Calculate totals for invoice
function calculateTotals() {
    let subtotal = 0;
    
    document.querySelectorAll('.item-row').forEach(function(row) {
        // Check if row is marked for deletion
        const deleteCheckbox = row.querySelector('input[type="checkbox"][name$="-DELETE"]');
        if (deleteCheckbox && deleteCheckbox.checked) {
            return; // Skip deleted rows
        }
        
        const quantityInput = row.querySelector('.item-quantity');
        const priceInput = row.querySelector('.item-price');
        const subtotalField = row.querySelector('.item-subtotal');
        
        if (quantityInput && priceInput && subtotalField) {
            const quantity = parseFloat(quantityInput.value) || 0;
            const price = parseFloat(priceInput.value) || 0;
            const itemSubtotal = quantity * price;
            
            subtotalField.value = itemSubtotal.toFixed(2);
            subtotal += itemSubtotal;
        }
    });
    
    // Get discount
    const discountField = document.querySelector('input[name="discount"]');
    const discount = discountField ? (parseFloat(discountField.value) || 0) : 0;
    
    // Calculate total
    const total = subtotal - discount;
    
    // Update display
    const subtotalDisplay = document.getElementById('invoice-subtotal');
    const totalDisplay = document.getElementById('invoice-total');
    
    if (subtotalDisplay) {
        subtotalDisplay.textContent = '$' + subtotal.toFixed(2);
    }
    if (totalDisplay) {
        totalDisplay.textContent = '$' + Math.max(0, total).toFixed(2);
    }
}

// Auto-dismiss alerts after 5 seconds
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-danger)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Utility function for AJAX requests (if needed in future)
function sendAjaxRequest(url, method, data, successCallback, errorCallback) {
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (successCallback) successCallback(data);
    })
    .catch(error => {
        if (errorCallback) errorCallback(error);
    });
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Confirm delete actions
document.addEventListener('click', function(e) {
    const deleteLink = e.target.closest('a[href*="delete"]');
    if (deleteLink && !deleteLink.closest('form')) {
        const confirmMessage = 'Are you sure you want to delete this item?';
        if (!confirm(confirmMessage)) {
            e.preventDefault();
        }
    }
});
