/**
 * StockPulse Pro - Enterprise Client Interactions & Theme Controller
 */

// 1. Theme Controller
function initTheme() {
    const savedTheme = localStorage.getItem('stockpulse_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButtonUI(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('stockpulse_theme', newTheme);
    updateThemeButtonUI(newTheme);
}

function updateThemeButtonUI(theme) {
    const btn = document.getElementById('themeToggleBtn');
    if (!btn) return;
    
    if (theme === 'light') {
        btn.innerHTML = '<i class="bi bi-moon text-secondary"></i> <span>Dark Mode</span>';
    } else {
        btn.innerHTML = '<i class="bi bi-sun text-secondary"></i> <span>Light Mode</span>';
    }
}

// 2. DOM Ready Initialization
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    
    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) {
        themeBtn.addEventListener('click', toggleTheme);
    }
    
    // Auto uppercase for ticker search inputs
    const tickerInputs = document.querySelectorAll('input[name="ticker"]');
    tickerInputs.forEach(input => {
        input.addEventListener('input', (e) => {
            e.target.value = e.target.value.toUpperCase();
        });
    });
});
