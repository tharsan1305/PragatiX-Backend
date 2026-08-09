// SQL Security Scanner Report JavaScript
(function() {
    'use strict';

    const DATA = window.REPORT_DATA || {};

    // Charts
    function initCharts() {
        const isDark = true;
        const textColor = '#c9d1d9';
        const gridColor = 'rgba(140, 149, 159, 0.1)';

        const commonOptions = {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: { color: textColor, font: { size: 11 } }
                }
            },
            scales: {
                x: { ticks: { color: textColor }, grid: { color: gridColor } },
                y: { ticks: { color: textColor }, grid: { color: gridColor } }
            }
        };

        // Severity Pie Chart
        const severityEl = document.getElementById('severityChart');
        if (severityEl && Object.keys(DATA.severity || {}).length) {
            const severityData = DATA.severity;
            const order = ['Critical', 'High', 'Medium', 'Low', 'Info'];
            const labels = order.filter(s => severityData[s]);
            const colors = {
                'Critical': '#f85149',
                'High': '#f0883e',
                'Medium': '#39c5cf',
                'Low': '#8b949e',
                'Info': '#58a6ff'
            };
            new Chart(severityEl, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: labels.map(l => severityData[l]),
                        backgroundColor: labels.map(l => colors[l] || '#58a6ff')
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: textColor, font: { size: 11 } }
                        }
                    }
                }
            });
        }

        // Category Bar Chart
        const categoryEl = document.getElementById('categoryChart');
        if (categoryEl && Object.keys(DATA.category || {}).length) {
            const categoryData = DATA.category;
            new Chart(categoryEl, {
                type: 'bar',
                data: {
                    labels: Object.keys(categoryData),
                    datasets: [{
                        label: 'Findings',
                        data: Object.values(categoryData),
                        backgroundColor: ['#f85149', '#d29922', '#58a6ff', '#3fb950', '#8b949e', '#bc8cff'].slice(0, Object.keys(categoryData).length)
                    }]
                },
                options: commonOptions
            });
        }

        // Object Types Donut Chart
        const objectEl = document.getElementById('objectChart');
        if (objectEl && Object.keys(DATA.objects || {}).length) {
            const objectData = DATA.objects;
            new Chart(objectEl, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(objectData),
                    datasets: [{
                        data: Object.values(objectData),
                        backgroundColor: ['#58a6ff', '#3fb950', '#d29922', '#f85149', '#bc8cff', '#39c5cf', '#8b949e']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: { color: textColor, font: { size: 11 } }
                        }
                    }
                }
            });
        }

        // Heatmap Chart (Top Risk Tables)
        const heatmapEl = document.getElementById('heatmapChart');
        if (heatmapEl && Object.keys(DATA.tableRisk || {}).length) {
            const tableRisk = DATA.tableRisk;
            const tables = Object.keys(tableRisk).slice(0, 15);
            const scores = tables.map(t => tableRisk[t]);
            const colors = scores.map(s => {
                if (s >= 80) return 'rgba(248, 81, 73, 0.85)';
                if (s >= 50) return 'rgba(242, 136, 62, 0.85)';
                if (s >= 25) return 'rgba(210, 153, 34, 0.85)';
                return 'rgba(63, 185, 80, 0.85)';
            });
            new Chart(heatmapEl, {
                type: 'bar',
                data: {
                    labels: tables,
                    datasets: [{
                        label: 'Risk Score',
                        data: scores,
                        backgroundColor: colors
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            max: 100,
                            ticks: { color: textColor },
                            grid: { color: gridColor }
                        },
                        y: {
                            ticks: {
                                color: textColor,
                                font: { size: 10 }
                            },
                            grid: { display: false }
                        }
                    }
                }
            });
        }

        // Files vs Issues Line Chart
        const filesEl = document.getElementById('filesChart');
        if (filesEl && Object.keys(DATA.filesIssues || {}).length) {
            const filesIssues = DATA.filesIssues;
            new Chart(filesEl, {
                type: 'line',
                data: {
                    labels: Object.keys(filesIssues),
                    datasets: [{
                        label: 'Issues',
                        data: Object.values(filesIssues),
                        borderColor: '#f85149',
                        backgroundColor: 'rgba(248, 81, 73, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: commonOptions
            });
        }
    }

    // DataTables initialization
    function initDataTables() {
        document.querySelectorAll('.findings-table').forEach(function(table) {
            if (typeof $ !== 'undefined' && typeof $.fn.DataTable !== 'undefined') {
                $(table).DataTable({
                    pageLength: 10,
                    responsive: true,
                    dom: '<"row mb-3"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
                         '<"row"<"col-sm-12"tr>>' +
                         '<"row mt-3"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>' +
                         'Bfrtip',
                    buttons: [
                        { extend: 'csv', text: 'Export CSV', className: 'btn btn-sm btn-outline-info me-1' },
                        { extend: 'excel', text: 'Export Excel', className: 'btn btn-sm btn-outline-success me-1' },
                        { extend: 'pdf', text: 'Export PDF', className: 'btn btn-sm btn-outline-danger me-1' },
                        { extend: 'print', text: 'Print', className: 'btn btn-sm btn-outline-secondary' }
                    ],
                    order: [[0, 'asc']],
                    columnDefs: [
                        { targets: [6, 7], orderable: false }
                    ]
                });
            }
        });
    }

    // Expand/collapse finding details
    function initExpanders() {
        document.addEventListener('click', function(e) {
            const btn = e.target.closest('.expand-btn');
            if (btn) {
                const target = document.getElementById(btn.dataset.target);
                if (target) {
                    const isVisible = target.style.display !== 'none';
                    target.style.display = isVisible ? 'none' : 'table-row';
                    btn.textContent = isVisible ? 'View' : 'Hide';
                    btn.classList.toggle('btn-outline-warning', !isVisible);
                }
            }
        });
    }

    // Object detail toggle
    function initObjectDetails() {
        document.addEventListener('click', function(e) {
            const btn = e.target.closest('.object-detail-btn');
            if (btn) {
                const target = document.getElementById('obj-detail-' + btn.dataset.obj);
                if (target) {
                    const isVisible = target.style.display !== 'none';
                    target.style.display = isVisible ? 'none' : 'block';
                    btn.textContent = isVisible ? 'View Details' : 'Hide Details';
                    btn.classList.toggle('btn-outline-warning', !isVisible);
                }
            }
        });
    }

    // Scrollspy for sidebar
    function initScrollspy() {
        const sections = document.querySelectorAll('.section');
        const navLinks = document.querySelectorAll('.sidebar .nav-link');
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    navLinks.forEach(function(link) {
                        link.classList.remove('active');
                        if (link.getAttribute('href') === '#' + entry.target.id) {
                            link.classList.add('active');
                        }
                    });
                }
            });
        }, { rootMargin: '-20% 0px -70% 0px' });
        sections.forEach(function(section) {
            observer.observe(section);
        });
    }

    // Initialize on load
    document.addEventListener('DOMContentLoaded', function() {
        initCharts();
        initDataTables();
        initExpanders();
        initObjectDetails();
        initScrollspy();
    });
})();
