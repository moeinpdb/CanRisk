/**
 * Charts Management
 * مدیریت نمودارها با Chart.js
 */

class ChartsManager {
    constructor() {
        this.charts = {};
        this.setupChartDefaults();
    }

    setupChartDefaults() {
        // تنظیمات پیش‌فرض Chart.js
        if (typeof Chart !== 'undefined') {
            Chart.defaults.font.family = 'Vazir, Inter, sans-serif';
            Chart.defaults.font.size = 13;
            Chart.defaults.color = '#374151';
            Chart.defaults.plugins.legend.rtl = true;
            Chart.defaults.plugins.tooltip.rtl = true;
        }
    }

    /**
     * نمودار مقایسه ریسک (Doughnut Chart)
     */
    createRiskComparisonChart(absoluteRisk, averageRisk) {
        const ctx = document.getElementById('riskComparisonChart');
        if (!ctx) return;

        // Destroy previous chart if exists
        if (this.charts.riskComparison) {
            this.charts.riskComparison.destroy();
        }

        const absolutePercent = (absoluteRisk * 100).toFixed(2);
        const averagePercent = (averageRisk * 100).toFixed(2);
        const noRisk = Math.max(0, 100 - parseFloat(absolutePercent));

        this.charts.riskComparison = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [
                    'ریسک شما',
                    'ریسک میانگین',
                    'بدون ریسک'
                ],
                datasets: [{
                    data: [absolutePercent, averagePercent, noRisk],
                    backgroundColor: [
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(16, 185, 129, 0.8)'
                    ],
                    borderColor: [
                        '#ef4444',
                        '#f59e0b',
                        '#10b981'
                    ],
                    borderWidth: 2,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: {
                                size: 14,
                                weight: '600'
                            },
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                label += context.parsed + '%';
                                return label;
                            }
                        },
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: { size: 14, weight: 'bold' },
                        bodyFont: { size: 13 },
                        padding: 12,
                        cornerRadius: 8
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 1500,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    /**
     * نمودار ریسک طول عمر (Line Chart)
     */
    createLifetimeRiskChart(currentAge, projectionAge, absoluteRisk5year, absoluteRiskLifetime) {
        const ctx = document.getElementById('lifetimeRiskChart');
        if (!ctx) return;

        // Destroy previous chart if exists
        if (this.charts.lifetimeRisk) {
            this.charts.lifetimeRisk.destroy();
        }

        // Create data points
        const ages = [];
        const risks = [];
        
        // Current age
        ages.push(currentAge);
        risks.push(0);
        
        // 5-year risk
        ages.push(currentAge + 5);
        risks.push((absoluteRisk5year * 100).toFixed(2));
        
        // 10-year estimation (interpolation)
        const risk10year = absoluteRisk5year + (absoluteRiskLifetime - absoluteRisk5year) * 0.3;
        ages.push(currentAge + 10);
        risks.push((risk10year * 100).toFixed(2));
        
        // Lifetime risk
        ages.push(Math.min(90, currentAge + 45));
        risks.push((absoluteRiskLifetime * 100).toFixed(2));

        this.charts.lifetimeRisk = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ages.map(age => `${age} سال`),
                datasets: [{
                    label: 'ریسک تجمعی',
                    data: risks,
                    fill: true,
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderColor: 'rgb(99, 102, 241)',
                    borderWidth: 3,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointBackgroundColor: '#fff',
                    pointBorderWidth: 3,
                    pointBorderColor: 'rgb(99, 102, 241)',
                    pointHoverBackgroundColor: 'rgb(99, 102, 241)',
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return 'ریسک: ' + context.parsed.y + '%';
                            },
                            title: function(context) {
                                return 'سن: ' + context[0].label;
                            }
                        },
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: { size: 14, weight: 'bold' },
                        bodyFont: { size: 13 },
                        padding: 12,
                        cornerRadius: 8
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            },
                            font: {
                                size: 12
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        title: {
                            display: true,
                            text: 'احتمال ابتلا (%)',
                            font: {
                                size: 13,
                                weight: 'bold'
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 12
                            }
                        },
                        title: {
                            display: true,
                            text: 'سن',
                            font: {
                                size: 13,
                                weight: 'bold'
                            }
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    /**
     * نمودار میله‌ای فاکتورهای ریسک
     */
    createRiskFactorsChart(factors) {
        const ctx = document.getElementById('riskFactorsChart');
        if (!ctx) return;

        if (this.charts.riskFactors) {
            this.charts.riskFactors.destroy();
        }

        const labels = factors.map(f => f.name);
        const values = factors.map(f => f.impact);
        const colors = values.map(v => {
            if (v > 0) return 'rgba(239, 68, 68, 0.8)'; // افزایش ریسک
            if (v < 0) return 'rgba(16, 185, 129, 0.8)'; // کاهش ریسک
            return 'rgba(156, 163, 175, 0.8)'; // خنثی
        });

        this.charts.riskFactors = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'تأثیر بر ریسک',
                    data: values,
                    backgroundColor: colors,
                    borderColor: colors.map(c => c.replace('0.8', '1')),
                    borderWidth: 2,
                    borderRadius: 8
                }]
            },
            options: {
                indexAxis: 'y', // Horizontal bar
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed.x;
                                return value > 0 
                                    ? `افزایش: +${value}%`
                                    : value < 0 
                                    ? `کاهش: ${value}%`
                                    : 'خنثی';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * نمودار مقایسه با میانگین (Radar Chart)
     */
    createComparisonRadarChart(userFactors, averageFactors) {
        const ctx = document.getElementById('comparisonRadarChart');
        if (!ctx) return;

        if (this.charts.comparisonRadar) {
            this.charts.comparisonRadar.destroy();
        }

        this.charts.comparisonRadar = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: [
                    'سن',
                    'سابقه بیوپسی',
                    'سن قاعدگی',
                    'سن زایمان',
                    'سابقه خانوادگی'
                ],
                datasets: [
                    {
                        label: 'شما',
                        data: userFactors,
                        fill: true,
                        backgroundColor: 'rgba(99, 102, 241, 0.2)',
                        borderColor: 'rgb(99, 102, 241)',
                        pointBackgroundColor: 'rgb(99, 102, 241)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgb(99, 102, 241)',
                        borderWidth: 2,
                        pointRadius: 4
                    },
                    {
                        label: 'میانگین',
                        data: averageFactors,
                        fill: true,
                        backgroundColor: 'rgba(156, 163, 175, 0.2)',
                        borderColor: 'rgb(156, 163, 175)',
                        pointBackgroundColor: 'rgb(156, 163, 175)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgb(156, 163, 175)',
                        borderWidth: 2,
                        pointRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            font: {
                                size: 11
                            }
                        },
                        pointLabels: {
                            font: {
                                size: 12,
                                weight: '600'
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: {
                                size: 13,
                                weight: '600'
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * پاک کردن تمام نمودارها
     */
    destroyAll() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }
}

// Initialize charts manager
window.ChartsManager = new ChartsManager();