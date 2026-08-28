/**
 * StockPulse Pro - Enterprise Client Interactions & Theme Controller
 */

// 1. Theme Controller
function initTheme() {
    const savedTheme = localStorage.getItem('stockpulse_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButtonUI(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
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

// 2. Simple One-Click Chart Timeframe & Zoom Controller
function getPlotlyChartElement() {
    return document.querySelector('.chart-wrapper .plotly-graph-div') || document.querySelector('.chart-wrapper > div');
}

function setChartRange(days, btnElement) {
    const gd = getPlotlyChartElement();
    if (!gd || !gd.data || !gd.data[0] || !window.Plotly) return;
    
    const totalPoints = gd.data[0].x.length;
    const startIndex = Math.max(0, totalPoints - days);
    const endIndex = totalPoints - 1;
    
    Plotly.relayout(gd, {
        'xaxis.range': [startIndex - 0.5, endIndex + 0.5],
        'xaxis2.range': [startIndex - 0.5, endIndex + 0.5]
    });
    
    if (btnElement) {
        document.querySelectorAll('#timeframe-buttons .chart-zoom-btn').forEach(b => b.classList.remove('active'));
        btnElement.classList.add('active');
    }
}

function zoomChartStep(direction) {
    const gd = getPlotlyChartElement();
    if (!gd || !gd.data || !gd.data[0] || !window.Plotly) return;
    
    const totalPoints = gd.data[0].x.length;
    let range = (gd.layout && gd.layout.xaxis && gd.layout.xaxis.range) ? [...gd.layout.xaxis.range] : [0, totalPoints - 1];
    
    let curStart = typeof range[0] === 'number' ? range[0] : 0;
    let curEnd = typeof range[1] === 'number' ? range[1] : totalPoints - 1;
    let span = curEnd - curStart;
    
    let step = Math.max(2, Math.round(span * 0.25));
    let newStart = curStart + (direction * step);
    
    if (newStart < -0.5) newStart = -0.5;
    if (curEnd - newStart < 6) newStart = curEnd - 6;
    
    Plotly.relayout(gd, {
        'xaxis.range': [newStart, curEnd],
        'xaxis2.range': [newStart, curEnd]
    });
}

function resetChartZoom() {
    const gd = getPlotlyChartElement();
    if (!gd || !window.Plotly) return;
    
    Plotly.relayout(gd, {
        'xaxis.autorange': true,
        'xaxis2.autorange': true
    });
    
    document.querySelectorAll('#timeframe-buttons .chart-zoom-btn').forEach(b => b.classList.remove('active'));
    const allBtn = document.querySelector('#timeframe-buttons .chart-zoom-btn[data-range="all"]');
    if (allBtn) allBtn.classList.add('active');
}

// 3. DOM Ready Initialization
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    
    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) {
        themeBtn.addEventListener('click', toggleTheme);
    }
    
    const tickerInputs = document.querySelectorAll('input[name="ticker"]');
    tickerInputs.forEach(input => {
        input.addEventListener('input', (e) => {
            e.target.value = e.target.value.toUpperCase();
        });
    });
});
