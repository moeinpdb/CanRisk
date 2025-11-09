/**
 * API Communication Module
 * ارتباط با Backend API
 */

const API_BASE_URL = 'http://localhost:8000';

const API = {
    /**
     * محاسبه ریسک Gail
     */
    async calculateRisk(formData) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/gail/calculate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail?.error || errorData.detail || 'خطا در محاسبه ریسک');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * دریافت اطلاعات مدل
     */
    async getModelInfo() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/gail/info`);
            
            if (!response.ok) {
                throw new Error('خطا در دریافت اطلاعات');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * دریافت لیست نژادها
     */
    async getRaces() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/gail/races`);
            
            if (!response.ok) {
                throw new Error('خطا در دریافت لیست نژادها');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * Health Check
     */
    async healthCheck() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/health`);
            
            if (!response.ok) {
                throw new Error('سرور در دسترس نیست');
            }

            return await response.json();
        } catch (error) {
            console.error('Health Check Failed:', error);
            throw error;
        }
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API;
}