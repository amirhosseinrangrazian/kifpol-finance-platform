/**
 * KifPool - Main JavaScript
 * Personal Finance Manager
 */

// ==================== 
// Persian Number Formatter
// ====================
function toPersianNumber(num) {
    const persianDigits = '۰۱۲۳۴۵۶۷۸۹';
    return num.toString().replace(/[0-9]/g, d => persianDigits[d]);
}

function formatAmount(amount) {
    return toPersianNumber(amount.toLocaleString());
}

// ==================== 
// Chart.js Default Config
// ====================
if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = 'Vazirmatn';
    Chart.defaults.color = '#78716c';
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
}

// ==================== 
// Theme Management
// ====================
function setTheme(themeId) {
    document.body.className = 'theme-' + themeId;
    localStorage.setItem('app-theme', themeId);
}

// ==================== 
// Alert Auto-dismiss
// ====================
document.addEventListener('DOMContentLoaded', function () {
    // Auto dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    });

    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));
});

// ==================== 
// Format Input Numbers
// ====================
document.addEventListener('input', function (e) {
    if (e.target.type === 'number' && e.target.value) {
        // Add thousand separators while typing (optional)
    }
});

// ==================== 
// CSRF Token for AJAX
// ====================
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

// ==================== 
// Loading States
// ====================
function showLoading(button) {
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> در حال پردازش...';
}

function hideLoading(button, originalText) {
    button.disabled = false;
    button.innerHTML = originalText;
}

console.log('🌿 KifPool - Personal Finance Manager');
