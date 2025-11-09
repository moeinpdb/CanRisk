/**
 * Wizard Form Management
 * مدیریت فرم چند مرحله‌ای
 */

class WizardManager {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 5;
        this.formData = {};
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateProgress();
        this.setupConditionalFields();
    }

    setupEventListeners() {
        // Navigation buttons
        document.getElementById('nextBtn')?.addEventListener('click', () => this.nextStep());
        document.getElementById('prevBtn')?.addEventListener('click', () => this.prevStep());
        document.getElementById('submitBtn')?.addEventListener('click', () => this.submitForm());

        // Start button
        document.getElementById('startAssessment')?.addEventListener('click', () => {
            this.showWizard();
        });

        // Form validation on change
        document.querySelectorAll('input, select').forEach(input => {
            input.addEventListener('change', (e) => this.validateField(e.target));
        });

        // Age slider sync
        const ageInput = document.getElementById('age');
        const ageSlider = document.getElementById('ageSlider');
        
        if (ageInput && ageSlider) {
            ageSlider.addEventListener('input', (e) => {
                ageInput.value = e.target.value;
            });
            
            ageInput.addEventListener('input', (e) => {
                ageSlider.value = e.target.value;
            });
        }
    }

    setupConditionalFields() {
        // Show/hide race subgroup
        const raceSelect = document.getElementById('race');
        const subraceGroup = document.getElementById('subraceGroup');
        
        raceSelect?.addEventListener('change', (e) => {
            if (e.target.value === '4') {
                subraceGroup.style.display = 'block';
                subraceGroup.classList.add('fade-in');
            } else {
                subraceGroup.style.display = 'none';
            }
        });

        // Show/hide biopsy details
        const biopsyRadios = document.querySelectorAll('input[name="ever_had_biopsy"]');
        const biopsyCountGroup = document.getElementById('biopsyCountGroup');
        const hyperplasiaGroup = document.getElementById('hyperplasiaGroup');
        
        biopsyRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                if (e.target.value === 'yes') {
                    biopsyCountGroup.style.display = 'block';
                    hyperplasiaGroup.style.display = 'block';
                    biopsyCountGroup.classList.add('fade-in');
                    hyperplasiaGroup.classList.add('fade-in');
                } else {
                    biopsyCountGroup.style.display = 'none';
                    hyperplasiaGroup.style.display = 'none';
                }
            });
        });

        // Cancer history warning
        const cancerRadios = document.querySelectorAll('input[name="has_breast_cancer_history"]');
        const cancerWarning = document.getElementById('cancerHistoryWarning');
        
        cancerRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                if (e.target.value === 'true') {
                    cancerWarning.style.display = 'flex';
                    cancerWarning.classList.add('fade-in');
                } else {
                    cancerWarning.style.display = 'none';
                }
            });
        });

        // Genetic mutation warning
        const geneticRadios = document.querySelectorAll('input[name="has_genetic_mutation"]');
        const geneticWarning = document.getElementById('geneticWarning');
        
        geneticRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                if (e.target.value === 'yes') {
                    geneticWarning.style.display = 'flex';
                    geneticWarning.classList.add('fade-in');
                } else {
                    geneticWarning.style.display = 'none';
                }
            });
        });
    }

    showWizard() {
        document.getElementById('heroSection').style.display = 'none';
        document.getElementById('wizardSection').style.display = 'block';
        document.getElementById('wizardSection').classList.add('fade-in');
        
        // Animate stats before hiding
        this.animateStats();
    }

    animateStats() {
        const stats = document.querySelectorAll('.stat-number');
        stats.forEach(stat => {
            const target = parseInt(stat.dataset.target);
            let current = 0;
            const increment = target / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    stat.textContent = target.toLocaleString('fa-IR');
                    clearInterval(timer);
                } else {
                    stat.textContent = Math.floor(current).toLocaleString('fa-IR');
                }
            }, 30);
        });
    }

    nextStep() {
        if (!this.validateCurrentStep()) {
            this.showToast('error', 'لطفاً تمام فیلدهای الزامی را تکمیل کنید');
            return;
        }

        if (this.currentStep < this.totalSteps) {
            this.saveStepData();
            
            // Hide current step
            const currentStepEl = document.querySelector(`.wizard-step[data-step="${this.currentStep}"]`);
            currentStepEl.classList.remove('active');
            currentStepEl.classList.add('fade-out');
            
            setTimeout(() => {
                currentStepEl.classList.remove('fade-out');
                this.currentStep++;
                
                // Show next step
                const nextStepEl = document.querySelector(`.wizard-step[data-step="${this.currentStep}"]`);
                nextStepEl.classList.add('active', 'fade-in');
                
                this.updateProgress();
                this.updateButtons();
            }, 300);
        }
    }

    prevStep() {
        if (this.currentStep > 1) {
            // Hide current step
            const currentStepEl = document.querySelector(`.wizard-step[data-step="${this.currentStep}"]`);
            currentStepEl.classList.remove('active');
            
            this.currentStep--;
            
            // Show previous step
            const prevStepEl = document.querySelector(`.wizard-step[data-step="${this.currentStep}"]`);
            prevStepEl.classList.add('active', 'fade-in');
            
            this.updateProgress();
            this.updateButtons();
        }
    }

    updateProgress() {
        const progress = (this.currentStep / this.totalSteps) * 100;
        document.getElementById('progressFill').style.width = `${progress}%`;
        
        // Update step indicators
        this.renderProgressSteps();
    }

    renderProgressSteps() {
        const stepsContainer = document.getElementById('progressSteps');
        const stepTitles = [
            'واجد شرایط بودن',
            'اطلاعات جمعیتی',
            'سابقه پزشکی',
            'سابقه باروری',
            'سابقه خانوادگی'
        ];
        
        stepsContainer.innerHTML = stepTitles.map((title, index) => {
            const stepNum = index + 1;
            let className = 'progress-step';
            if (stepNum < this.currentStep) className += ' completed';
            if (stepNum === this.currentStep) className += ' active';
            
            return `
                <div class="${className}">
                    <div class="step-circle">
                        <span class="step-number">${stepNum}</span>
                        <i class="fas fa-check"></i>
                    </div>
                    <span class="step-label">${title}</span>
                </div>
            `;
        }).join('');
    }

    updateButtons() {
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const submitBtn = document.getElementById('submitBtn');
        
        // Show/hide previous button
        prevBtn.style.display = this.currentStep === 1 ? 'none' : 'inline-flex';
        
        // Show/hide next vs submit
        if (this.currentStep === this.totalSteps) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'inline-flex';
        } else {
            nextBtn.style.display = 'inline-flex';
            submitBtn.style.display = 'none';
        }
    }

    validateCurrentStep() {
        const currentStepEl = document.querySelector(`.wizard-step[data-step="${this.currentStep}"]`);
        const requiredFields = currentStepEl.querySelectorAll('[required]');
        
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        
        // Remove previous error
        field.classList.remove('error');
        
        // Check if required and empty
        if (field.hasAttribute('required') && !value) {
            isValid = false;
        }
        
        // Age validation
        if (field.id === 'age') {
            const age = parseInt(value);
            if (age < 35 || age > 85) {
                isValid = false;
                this.showToast('error', 'سن باید بین 35 تا 85 سال باشد');
            }
        }
        
        if (!isValid) {
            field.classList.add('error');
        }
        
        return isValid;
    }

    saveStepData() {
        const currentStepEl = document.querySelector(`.wizard-step[data-step="${this.currentStep}"]`);
        const inputs = currentStepEl.querySelectorAll('input, select');
        
        inputs.forEach(input => {
            if (input.type === 'radio') {
                if (input.checked) {
                    this.formData[input.name] = input.value;
                }
            } else {
                this.formData[input.name] = input.value;
            }
        });
    }

    async submitForm() {
        if (!this.validateCurrentStep()) {
            this.showToast('error', 'لطفاً تمام فیلدهای الزامی را تکمیل کنید');
            return;
        }
        
        this.saveStepData();
        
        // Show loading
        this.showLoading(true);
        
        // Prepare data for API
        const apiData = this.prepareAPIData();
        
        try {
            const result = await API.calculateRisk(apiData);
            
            // Hide loading
            this.showLoading(false);
            
            // Show results
            this.showResults(result);
            
        } catch (error) {
            this.showLoading(false);
            this.showToast('error', error.message || 'خطا در محاسبه ریسک. لطفاً دوباره تلاش کنید.');
        }
    }

    prepareAPIData() {
        return {
            has_breast_cancer_history: this.formData.has_breast_cancer_history === 'true',
            has_genetic_mutation: this.formData.has_genetic_mutation || 'unknown',
            age: parseInt(this.formData.age),
            race: parseInt(this.formData.race),
            sub_race: this.formData.sub_race ? parseInt(this.formData.sub_race) : null,
            ever_had_biopsy: this.formData.ever_had_biopsy || 'unknown',
            number_of_biopsies: this.formData.number_of_biopsies ? parseInt(this.formData.number_of_biopsies) : null,
            has_atypical_hyperplasia: this.formData.has_atypical_hyperplasia || 'unknown',
            age_at_menarche: parseInt(this.formData.age_at_menarche),
            age_at_first_birth: this.formData.age_at_first_birth === 'null' ? null : parseInt(this.formData.age_at_first_birth),
            num_first_degree_relatives: parseInt(this.formData.num_first_degree_relatives)
        };
    }

    showResults(result) {
        // Hide wizard, show results
        document.getElementById('wizardSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';
        document.getElementById('resultsSection').classList.add('fade-in');
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        // Populate results
        if (window.ResultsManager) {
            window.ResultsManager.displayResults(result, this.formData);
        }
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        const submitBtn = document.getElementById('submitBtn');
        const spinner = submitBtn.querySelector('.spinner');
        
        if (show) {
            overlay.style.display = 'flex';
            submitBtn.disabled = true;
            spinner.style.display = 'inline-block';
        } else {
            overlay.style.display = 'none';
            submitBtn.disabled = false;
            spinner.style.display = 'none';
        }
    }

    showToast(type, message) {
        const container = document.getElementById('toastContainer');
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-times-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="fas ${icons[type]}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Initialize wizard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.wizardManager = new WizardManager();
});