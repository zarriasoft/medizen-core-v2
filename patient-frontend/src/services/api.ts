import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    timeout: 10000,
});

// Interceptor to attach token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('patient_token');
    if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

export const authApi = {
    login: async (email: string, password: string) => {
        const formData = new URLSearchParams();
        formData.append('username', email); // OAuth2 expects 'username'
        formData.append('password', password);

        const response = await api.post('/auth/login/patient', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        return response.data;
    }
};

export const patientApi = {
    getProfile: () => api.get('/me/'),
    updateProfile: (data: Record<string, unknown>) => api.put('/me/', data),
    getMemberships: () => api.get('/me/memberships'),
    getAppointments: () => api.get('/me/appointments'),
    getAvailability: (date: string) => api.get(`/me/appointments/availability?target_date=${date}`),
    bookAppointment: (data: {appointment_date: string, membership_id?: number, notes?: string}) => api.post('/me/appointments', data),
    cancelAppointment: (id: number) => api.put(`/me/appointments/${id}/cancel`)
};

export const publicApi = {
    getPlans: () => api.get('/membership-plans/'),
    enroll: (data: Record<string, unknown>) => api.post('/public/enroll', data)
};

export default api;
