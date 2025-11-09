/**
 * PDF Export Module
 * تولید و دانلود گزارش PDF
 */

class PDFExporter {
    constructor() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.getElementById('downloadPdfBtn')?.addEventListener('click', () => {
            this.generatePDF();
        });

        document.getElementById('printBtn')?.addEventListener('click', () => {
            this.print();
        });
    }

    /**
     * تولید PDF از صفحه نتایج
     */
    async generatePDF() {
        try {
            // Show loading
            this.showLoading(true);

            const { jsPDF } = window.jspdf;
            const doc = new jsPDF({
                orientation: 'portrait',
                unit: 'mm',
                format: 'a4'
            });

            // Add Persian font support (if available)
            // Note: You need to add Persian font to jsPDF
            
            // Add title
            doc.setFontSize(20);
            doc.setTextColor(99, 102, 241);
            doc.text('Breast Cancer Risk Assessment Report', 105, 20, { align: 'center' });
            doc.text('گزارش ارزیابی ریسک سرطان سینه', 105, 30, { align: 'center' });

            // Add date
            doc.setFontSize(10);
            doc.setTextColor(100);
            const date = new Date().toLocaleDateString('fa-IR');
            doc.text(`تاریخ: ${date}`, 105, 40, { align: 'center' });

            // Line separator
            doc.setDrawColor(200);
            doc.line(20, 45, 190, 45);

            let yPos = 55;

            // Patient Summary
            doc.setFontSize(14);
            doc.setTextColor(0);
            doc.text('Patient Information / اطلاعات بیمار', 20, yPos);
            yPos += 10;

            const patientInfo = this.getPatientSummary();
            doc.setFontSize(11);
            patientInfo.forEach(info => {
                doc.text(`${info.label}: ${info.value}`, 25, yPos);
                yPos += 7;
            });

            yPos += 5;
            doc.line(20, yPos, 190, yPos);
            yPos += 10;

            // Risk Results
            doc.setFontSize(14);
            doc.setTextColor(0);
            doc.text('Risk Assessment Results / نتایج ارزیابی', 20, yPos);
            yPos += 10;

            const riskResults = this.getRiskResults();
            doc.setFontSize(11);
            
            // 5-Year Risk (highlighted box)
            doc.setFillColor(99, 102, 241);
            doc.rect(20, yPos, 170, 15, 'F');
            doc.setTextColor(255);
            doc.setFontSize(12);
            doc.text(`5-Year Absolute Risk: ${riskResults.absolute5year}`, 25, yPos + 10);
            yPos += 20;

            // Other results
            doc.setTextColor(0);
            doc.setFontSize(11);
            doc.text(`5-Year Average Risk: ${riskResults.average5year}`, 25, yPos);
            yPos += 7;
            doc.text(`Relative Risk: ${riskResults.relative5year}`, 25, yPos);
            yPos += 7;
            doc.text(`Risk Category: ${riskResults.category}`, 25, yPos);
            yPos += 10;

            // Lifetime Risk
            if (riskResults.absoluteLifetime) {
                doc.text(`Lifetime Risk (to age 90): ${riskResults.absoluteLifetime}`, 25, yPos);
                yPos += 10;
            }

            yPos += 5;
            doc.line(20, yPos, 190, yPos);
            yPos += 10;

            // Interpretation
            doc.setFontSize(14);
            doc.text('Interpretation / تفسیر', 20, yPos);
            yPos += 10;

            doc.setFontSize(10);
            const interpretation = this.getInterpretation();
            const splitInterpretation = doc.splitTextToSize(interpretation, 170);
            doc.text(splitInterpretation, 25, yPos);
            yPos += splitInterpretation.length * 5 + 10;

            // Recommendations (new page if needed)
            if (yPos > 240) {
                doc.addPage();
                yPos = 20;
            }

            doc.setFontSize(14);
            doc.text('Recommendations / توصیه‌ها', 20, yPos);
            yPos += 10;

            doc.setFontSize(10);
            const recommendations = this.getRecommendations();
            recommendations.forEach((rec, index) => {
                if (yPos > 270) {
                    doc.addPage();
                    yPos = 20;
                }
                
                const recText = `${index + 1}. ${rec}`;
                const splitRec = doc.splitTextToSize(recText, 165);
                doc.text(splitRec, 25, yPos);
                yPos += splitRec.length * 5 + 3;
            });

            // Add disclaimer at the bottom of last page
            const pageCount = doc.internal.getNumberOfPages();
            doc.setPage(pageCount);
            
            yPos = 270;
            doc.setFillColor(255, 243, 199);
            doc.rect(20, yPos, 170, 20, 'F');
            doc.setFontSize(8);
            doc.setTextColor(146, 64, 14);
            const disclaimer = 'Disclaimer: This is a statistical estimate and should not replace professional medical advice. Please consult with your healthcare provider.';
            const splitDisclaimer = doc.splitTextToSize(disclaimer, 165);
            doc.text(splitDisclaimer, 22, yPos + 5);

            // Add footer
            for (let i = 1; i <= pageCount; i++) {
                doc.setPage(i);
                doc.setFontSize(8);
                doc.setTextColor(150);
                doc.text(`Page ${i} of ${pageCount}`, 105, 290, { align: 'center' });
                doc.text('Gail Risk Calculator v1.4.2', 105, 294, { align: 'center' });
            }

            // Save PDF
            const filename = `Gail_Risk_Report_${Date.now()}.pdf`;
            doc.save(filename);

            this.showLoading(false);
            this.showToast('success', 'گزارش PDF با موفقیت دانلود شد');

        } catch (error) {
            console.error('PDF Generation Error:', error);
            this.showLoading(false);
            this.showToast('error', 'خطا در تولید PDF');
        }
    }

    /**
     * چاپ صفحه نتایج
     */
    print() {
        window.print();
    }

    /**
     * دریافت خلاصه اطلاعات بیمار
     */
    getPatientSummary() {
        const summaryItems = document.querySelectorAll('.summary-item');
        const summary = [];
        
        summaryItems.forEach(item => {
            const label = item.querySelector('.summary-label')?.textContent;
            const value = item.querySelector('.summary-value')?.textContent;
            if (label && value) {
                summary.push({ label, value });
            }
        });
        
        return summary;
    }

    /**
     * دریافت نتایج ریسک
     */
    getRiskResults() {
        return {
            absolute5year: document.getElementById('absoluteRisk5year')?.textContent || 'N/A',
            average5year: document.getElementById('averageRisk5year')?.textContent || 'N/A',
            relative5year: document.getElementById('relativeRisk5year')?.textContent || 'N/A',
            category: document.getElementById('riskBadge')?.textContent || 'N/A',
            absoluteLifetime: document.querySelector('.comparison-item:nth-child(1) .value')?.textContent
        };
    }

    /**
     * دریافت تفسیر نتایج
     */
    getInterpretation() {
        return document.getElementById('interpretationText')?.textContent || '';
    }

    /**
     * دریافت توصیه‌ها
     */
    getRecommendations() {
        const recommendations = [];
        const recItems = document.querySelectorAll('.recommendation-text');
        
        recItems.forEach(item => {
            recommendations.push(item.textContent);
        });
        
        return recommendations;
    }

    showLoading(show) {
        const btn = document.getElementById('downloadPdfBtn');
        if (show) {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> در حال تولید...';
        } else {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-file-pdf"></i> دانلود PDF';
        }
    }

    showToast(type, message) {
        if (window.wizardManager) {
            window.wizardManager.showToast(type, message);
        }
    }
}

// Initialize PDF exporter
document.addEventListener('DOMContentLoaded', () => {
    window.PDFExporter = new PDFExporter();
});