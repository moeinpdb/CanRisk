/**
 * Main Application Logic
 * منطق اصلی برنامه
 */

// Theme Management
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme();
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.getElementById('themeToggle')?.addEventListener('click', () => {
            this.toggleTheme();
        });
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        this.applyTheme();
        localStorage.setItem('theme', this.theme);
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        
        const icon = document.querySelector('#themeToggle i');
        if (icon) {
            icon.className = this.theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
    }
}

// Results Manager
class ResultsManager {
    displayResults(apiResult, formData) {
        // Patient Summary
        this.renderPatientSummary(apiResult.patient_info, formData);
        
        // Risk Score Card
        this.renderRiskScore(apiResult.risk_assessment);
        
        // Charts
        this.renderCharts(apiResult);
        
        // Risk Factors
        this.renderRiskFactors(formData, apiResult.risk_assessment);
        
        // Interpretation
        this.renderInterpretation(apiResult.risk_assessment);
        
        // Recommendations
        this.renderRecommendations(apiResult.risk_assessment);
        
        // Disclaimer
        this.renderDisclaimer(apiResult.disclaimer);
        
        // Setup back button
        this.setupBackButton();
    }

    renderPatientSummary(patientInfo, formData) {
        const container = document.getElementById('patientSummary');
        
        const summaryHTML = `
            <div class="summary-item fade-in">
                <div class="summary-label">
                    <i class="fas fa-calendar"></i> سن
                </div>
                <div class="summary-value">${patientInfo.age} سال</div>
            </div>
            <div class="summary-item fade-in delay-100">
                <div class="summary-label">
                    <i class="fas fa-globe"></i> نژاد
                </div>
                <div class="summary-value">${patientInfo.race_name_fa}</div>
            </div>
            <div class="summary-item fade-in delay-200">
                <div class="summary-label">
                    <i class="fas fa-chart-line"></i> بازه 5 ساله
                </div>
                <div class="summary-value">${patientInfo.age} - ${patientInfo.projection_age_5year} سال</div>
            </div>
            <div class="summary-item fade-in delay-300">
                <div class="summary-label">
                    <i class="fas fa-infinity"></i> بازه طول عمر
                </div>
                <div class="summary-value">تا ${patientInfo.projection_age_lifetime} سالگی</div>
            </div>
        `;
        
        container.innerHTML = summaryHTML;
    }

    renderRiskScore(assessment) {
        // Risk Badge
        const badge = document.getElementById('riskBadge');
        const category = assessment.risk_category;
        let badgeClass = 'medium';
        
        if (category === 'پایین') badgeClass = 'low';
        else if (category === 'بالا') badgeClass = 'high';
        
        badge.className = `risk-badge ${badgeClass}`;
        badge.textContent = category;
        
        // Risk Percentage (animated count up)
        const riskPercent = (assessment.absolute_risk_5year * 100).toFixed(2);
        this.animateNumber('absoluteRisk5year', 0, riskPercent, 2000);
        
        // Average Risk
        const avgPercent = (assessment.average_risk_5year * 100).toFixed(2);
        document.getElementById('averageRisk5year').textContent = avgPercent + '%';
        
        // Relative Risk
        const relRisk = assessment.relative_risk_5year.toFixed(2);
        document.getElementById('relativeRisk5year').textContent = relRisk + 'x';
        
        // Change card color based on risk level
        const card = document.getElementById('riskScoreCard');
        if (category === 'بالا') {
            card.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
        } else if (category === 'پایین') {
            card.style.background = 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)';
        }
    }

    animateNumber(elementId, start, end, duration) {
        const element = document.querySelector(`#${elementId} .percentage-number`);
        if (!element) return;
        
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                element.textContent = parseFloat(end).toFixed(2);
                clearInterval(timer);
            } else {
                element.textContent = current.toFixed(2);
            }
        }, 16);
    }

    renderCharts(apiResult) {
        const assessment = apiResult.risk_assessment;
        const patientInfo = apiResult.patient_info;
        
        // Risk Comparison Chart
        window.ChartsManager.createRiskComparisonChart(
            assessment.absolute_risk_5year,
            assessment.average_risk_5year
        );
        
        // Lifetime Risk Chart
        window.ChartsManager.createLifetimeRiskChart(
            patientInfo.age,
            patientInfo.projection_age_5year,
            assessment.absolute_risk_5year,
            assessment.absolute_risk_lifetime || assessment.absolute_risk_5year
        );
    }

    renderRiskFactors(formData, assessment) {
        const container = document.getElementById('riskFactorsBreakdown');
        
        const factors = this.analyzeRiskFactors(formData, assessment);
        
        const factorsHTML = factors.map((factor, index) => `
            <div class="factor-item fade-in-left delay-${index * 100}">
                <div class="factor-icon ${factor.type}">
                    <i class="fas ${factor.icon}"></i>
                </div>
                <div class="factor-content">
                    <div class="factor-name">${factor.name}</div>
                    <div class="factor-description">${factor.description}</div>
                </div>
                <div class="factor-impact ${factor.type}">
                    ${factor.impact}
                </div>
            </div>
        `).join('');
        
        container.innerHTML = factorsHTML;
    }

    analyzeRiskFactors(formData, assessment) {
        const factors = [];
        
        // Age
        const age = parseInt(formData.age);
        if (age >= 50) {
            factors.push({
                name: 'سن',
                description: `${age} سال - افزایش ریسک با افزایش سن`,
                impact: '+متوسط',
                type: 'negative',
                icon: 'fa-calendar-alt'
            });
        } else {
            factors.push({
                name: 'سن',
                description: `${age} سال - سن پایین‌تر`,
                impact: 'خنثی',
                type: 'neutral',
                icon: 'fa-calendar-alt'
            });
        }
        
        // Biopsy
        if (formData.ever_had_biopsy === 'yes') {
            const count = parseInt(formData.number_of_biopsies) || 1;
            factors.push({
                name: 'سابقه بیوپسی',
                description: `${count} بار بیوپسی - افزایش ریسک`,
                impact: count > 1 ? '+بالا' : '+متوسط',
                type: 'negative',
                icon: 'fa-microscope'
            });
        } else {
            factors.push({
                name: 'سابقه بیوپسی',
                description: 'بدون بیوپسی قبلی',
                impact: 'خنثی',
                type: 'positive',
                icon: 'fa-microscope'
            });
        }
        
        // Hyperplasia
        if (formData.has_atypical_hyperplasia === 'yes') {
            factors.push({
                name: 'هایپرپلازیا آتیپیک',
                description: 'وجود هایپرپلازیا در بیوپسی - افزایش قابل توجه ریسک',
                impact: '+خیلی بالا',
                type: 'negative',
                icon: 'fa-exclamation-triangle'
            });
        }
        
        // Family History
        const relatives = parseInt(formData.num_first_degree_relatives) || 0;
        if (relatives > 0) {
            factors.push({
                name: 'سابقه خانوادگی',
                description: `${relatives} بستگان درجه یک مبتلا - افزایش ریسک`,
                impact: relatives > 1 ? '+خیلی بالا' : '+بالا',
                type: 'negative',
                icon: 'fa-users'
            });
        } else {
            factors.push({
                name: 'سابقه خانوادگی',
                description: 'بدون سابقه خانوادگی',
                impact: 'خنثی',
                type: 'positive',
                icon: 'fa-users'
            });
        }
        
        // Menarche Age
        const menarcheAge = parseInt(formData.age_at_menarche);
        if (menarcheAge < 12) {
            factors.push({
                name: 'سن قاعدگی',
                description: 'قاعدگی زودرس - افزایش جزئی ریسک',
                impact: '+پایین',
                type: 'negative',
                icon: 'fa-venus'
            });
        }
        
        // First Birth Age
        const birthAge = formData.age_at_first_birth;
        if (birthAge === 'null') {
            factors.push({
                name: 'زایمان',
                description: 'بدون فرزند - افزایش جزئی ریسک',
                impact: '+پایین',
                type: 'negative',
                icon: 'fa-baby'
            });
        } else if (parseInt(birthAge) >= 30) {
            factors.push({
                name: 'سن اولین زایمان',
                description: 'زایمان در سن بالا - افزایش جزئی ریسک',
                impact: '+پایین',
                type: 'negative',
                icon: 'fa-baby'
            });
        }
        
        return factors;
    }

    renderInterpretation(assessment) {
        const container = document.getElementById('interpretationText');
        container.innerHTML = `<p>${assessment.interpretation_fa}</p>`;
        container.classList.add('fade-in');
    }

    renderRecommendations(assessment) {
        const container = document.getElementById('recommendationsList');
        
        const recsHTML = assessment.recommendations_fa.map((rec, index) => {
            const isHighPriority = rec.includes('⚠️');
            return `
                <div class="recommendation-item ${isHighPriority ? 'high-priority' : ''} fade-in-up delay-${index * 100}">
                    <div class="recommendation-icon">
                        <i class="fas ${isHighPriority ? 'fa-exclamation-circle' : 'fa-check-circle'}"></i>
                    </div>
                    <div class="recommendation-text">${rec.replace('⚠️', '')}</div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = recsHTML;
    }

    renderDisclaimer(disclaimerText) {
        document.getElementById('disclaimerText').textContent = disclaimerText;
    }

    setupBackButton() {
        document.getElementById('backToForm')?.addEventListener('click', () => {
            location.reload();
        });
    }
}

// Share functionality
class ShareManager {
    constructor() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.getElementById('shareBtn')?.addEventListener('click', () => {
            this.share();
        });
    }

    async share() {
        const shareData = {
            title: 'گزارش ارزیابی ریسک سرطان سینه',
            text: 'من ریسک سرطان سینه خود را با ابزار Gail محاسبه کردم',
            url: window.location.href
        };

        try {
            if (navigator.share) {
                await navigator.share(shareData);
            } else {
                // Fallback: Copy to clipboard
                await navigator.clipboard.writeText(window.location.href);
                this.showToast('success', 'لینک کپی شد');
            }
        } catch (error) {
            console.error('Share failed:', error);
        }
    }

    showToast(type, message) {
        if (window.wizardManager) {
            window.wizardManager.showToast(type, message);
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize managers
    window.themeManager = new ThemeManager();
    window.ResultsManager = new ResultsManager();
    window.shareManager = new ShareManager();
    
    // Check API health on load
    API.healthCheck()
        .then(health => {
            console.log('✅ API Status:', health);
        })
        .catch(error => {
            console.error('❌ API Connection Failed:', error);
            // Show warning to user
            const toast = document.createElement('div');
            toast.className = 'toast error';
            toast.innerHTML = `
                <i class="fas fa-exclamation-circle"></i>
                <span>خطا در اتصال به سرور. لطفاً اطمینان حاصل کنید که backend در حال اجراست.</span>
            `;
            document.getElementById('toastContainer')?.appendChild(toast);
        });
    
    // Add smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// Handle errors globally
window.addEventListener('error', (event) => {
    console.error('Global Error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled Promise Rejection:', event.reason);
});