/**
 * StockPulse Pro - Enterprise Client Interactions & Theme Controller
 */

// 1. Theme Controller
function initTheme() {
    const savedTheme = localStorage.getItem('stockpulse_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButtonUI(savedTheme);
    setTimeout(() => updatePlotlyTheme(savedTheme), 100);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('stockpulse_theme', newTheme);
    updateThemeButtonUI(newTheme);
    updatePlotlyTheme(newTheme);
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

function updatePlotlyTheme(theme) {
    const gd = getPlotlyChartElement();
    if (!gd || !window.Plotly) return;
    
    const isDark = theme === 'dark';
    const textColor = isDark ? '#cbd5e1' : '#475569';
    const gridColor = isDark ? 'rgba(148, 163, 184, 0.08)' : 'rgba(100, 116, 139, 0.12)';
    const hoverBg = isDark ? '#0c2d33' : '#ffffff';
    const hoverText = isDark ? '#ffffff' : '#0d1e16';
    const hoverBorder = isDark ? '#2A835F' : '#216a4c';
    
    Plotly.relayout(gd, {
        'font.color': textColor,
        'xaxis.tickfont.color': textColor,
        'xaxis.gridcolor': gridColor,
        'xaxis2.tickfont.color': textColor,
        'xaxis2.gridcolor': gridColor,
        'yaxis.tickfont.color': textColor,
        'yaxis.gridcolor': gridColor,
        'yaxis2.tickfont.color': textColor,
        'yaxis2.gridcolor': gridColor,
        'hoverlabel.bgcolor': hoverBg,
        'hoverlabel.font.color': hoverText,
        'hoverlabel.bordercolor': hoverBorder
    });
}

function updateIDXMarketClock() {
    const dotEl = document.getElementById('marketStatusDot');
    const statusEl = document.getElementById('marketStatusText');
    const clockEl = document.getElementById('idxClockText');
    if (!clockEl || !statusEl || !dotEl) return;

    const now = new Date();
    const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
    const wibDate = new Date(utc + (3600000 * 7));

    const day = wibDate.getDay();
    const hours = wibDate.getHours();
    const minutes = wibDate.getMinutes();
    const seconds = wibDate.getSeconds();
    const timeVal = hours * 60 + minutes;

    const timeStr = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')} WIB`;
    clockEl.textContent = timeStr;

    let isOpen = false;
    let statusLabel = 'PASAR TUTUP';

    if (day >= 1 && day <= 5) {
        if (day === 5) {
            if (timeVal >= 540 && timeVal < 690) {
                isOpen = true;
                statusLabel = 'SESI I AKTIF';
            } else if (timeVal >= 690 && timeVal < 840) {
                isOpen = false;
                statusLabel = 'ISTIRAHAT SESI';
            } else if (timeVal >= 840 && timeVal < 950) {
                isOpen = true;
                statusLabel = 'SESI II AKTIF';
            }
        } else {
            if (timeVal >= 540 && timeVal < 690) {
                isOpen = true;
                statusLabel = 'SESI I AKTIF';
            } else if (timeVal >= 690 && timeVal < 810) {
                isOpen = false;
                statusLabel = 'ISTIRAHAT SESI';
            } else if (timeVal >= 810 && timeVal < 950) {
                isOpen = true;
                statusLabel = 'SESI II AKTIF';
            }
        }
    }

    if (isOpen) {
        dotEl.className = 'market-status-dot online';
        statusEl.textContent = statusLabel;
        statusEl.className = 'text-success';
    } else {
        dotEl.className = 'market-status-dot offline';
        statusEl.textContent = statusLabel;
        statusEl.className = 'text-theme-muted';
    }
}

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

function showLoading(text) {
    const screen = document.getElementById('globalLoadingScreen');
    const bar = document.getElementById('topLoadingBar');
    const statusText = document.querySelector('.loading-status-text');
    if (text && statusText) {
        statusText.textContent = text;
    }
    if (bar) {
        bar.classList.remove('finish');
        bar.classList.add('active');
    }
    if (screen) {
        screen.classList.add('active');
    }
}

function hideLoading() {
    const screen = document.getElementById('globalLoadingScreen');
    const bar = document.getElementById('topLoadingBar');
    if (bar) {
        bar.classList.remove('active');
        bar.classList.add('finish');
    }
    if (screen) {
        screen.classList.remove('active');
    }
}

window.addEventListener('pageshow', () => {
    hideLoading();
});

window.addEventListener('load', () => {
    hideLoading();
});

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    hideLoading();
    updateIDXMarketClock();
    setInterval(updateIDXMarketClock, 1000);
    
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

    const searchForms = document.querySelectorAll('form');
    searchForms.forEach(f => {
        f.addEventListener('submit', () => {
            showLoading('MEMUAT ANALISIS SAHAM...');
        });
    });

    document.querySelectorAll('.quick-ticker-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            showLoading('MEMUAT DATA SAHAM...');
        });
    });

    document.querySelectorAll('.screener-btn-analisis').forEach(btn => {
        btn.addEventListener('click', () => {
            showLoading('MENYIAPKAN DASHBOARD...');
        });
    });

    const refreshBtn = document.querySelector('.btn-refresh-screener');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            showLoading('MEMINDAI 764 SAHAM IHSG...');
        });
    }

    document.querySelectorAll('.enterprise-nav-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            if (!tab.classList.contains('active')) {
                showLoading('MEMUAT HALAMAN...');
            }
        });
    });
});
