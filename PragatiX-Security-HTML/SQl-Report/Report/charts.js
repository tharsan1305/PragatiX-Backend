// SQL Security Scanner - Chart.js Configurations
// Helper for chart color schemes
const CHART_COLORS = {
    critical: '#f85149',
    high: '#f0883e',
    medium: '#39c5cf',
    low: '#8b949e',
    info: '#58a6ff',
    security: '#f85149',
    performance: '#d29922',
    schema: '#58a6ff',
    dataQuality: '#3fb950',
    bestPractices: '#8b949e',
    maintainability: '#bc8cff'
};

const CHART_DEFAULTS = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                color: '#c9d1d9',
                font: { size: 11 }
            }
        }
    }
};

function makePieChart(canvasId, labels, data, colors) {
    const el = document.getElementById(canvasId);
    if (!el) return;
    new Chart(el, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors
            }]
        },
        options: {
            ...CHART_DEFAULTS,
            plugins: {
                ...CHART_DEFAULTS.plugins,
                legend: { ...CHART_DEFAULTS.plugins.legend, position: 'bottom' }
            }
        }
    });
}

function makeBarChart(canvasId, labels, data, label, color) {
    const el = document.getElementById(canvasId);
    if (!el) return;
    new Chart(el, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label || 'Findings',
                data: data,
                backgroundColor: color || 'rgba(88, 166, 255, 0.8)'
            }]
        },
        options: {
            ...CHART_DEFAULTS,
            scales: {
                x: {
                    ticks: { color: '#c9d1d9' },
                    grid: { color: 'rgba(140, 149, 159, 0.1)' }
                },
                y: {
                    ticks: { color: '#c9d1d9' },
                    grid: { color: 'rgba(140, 149, 159, 0.1)' },
                    beginAtZero: true
                }
            }
        }
    });
}
