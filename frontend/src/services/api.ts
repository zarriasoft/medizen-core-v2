/// <reference types="vite/client" />
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
        'Bypass-Tunnel-Reminder': 'true'
    },
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export interface Patient {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    phone?: string;
    address?: string;
    date_of_birth?: string;
    created_at: string;
    is_active: boolean;
    ieim_records?: IeimRecord[];
}

export interface IeimRecord {
    id: number;
    patient_id: number;
    record_date: string;
    pain_level: number;
    sleep_quality: number;
    energy_level: number;
    stress_anxiety: number;
    mobility: number;
    inflammation: number;
    overall_score: number;
}

export const patientsApi = {
    getAll: async () => {
        const response = await api.get<Patient[]>('/patients/');
        return response.data;
    },
    getOne: async (id: number) => {
        const response = await api.get<Patient>(`/patients/${id}`);
        return response.data;
    },
    create: async (data: Omit<Patient, 'id' | 'created_at' | 'is_active'>) => {
        const response = await api.post<Patient>('/patients/', data);
        return response.data;
    },
    getIeimRecords: async (patientId: number) => {
        const response = await api.get<IeimRecord[]>(`/patients/${patientId}/ieim/`);
        return response.data;
    },
    addIeimRecord: async (patientId: number, data: Omit<IeimRecord, 'id' | 'patient_id' | 'record_date' | 'overall_score'>) => {
        const payload = { ...data, patient_id: patientId };
        const response = await api.post<IeimRecord>(`/patients/${patientId}/ieim/`, payload);
        return response.data;
    },
    update: async (id: number, data: any) => {
        const response = await api.put<Patient>(`/patients/${id}`, data);
        return response.data;
    },
    delete: async (id: number) => {
        const response = await api.delete(`/patients/${id}`);
        return response.data;
    }
};

export const membershipsApi = {
    getAll: async () => {
        const response = await api.get('/memberships/');
        return response.data;
    },
    getPatientMemberships: async (patientId: number) => {
        const response = await api.get(`/memberships/patient/${patientId}`);
        return response.data;
    },
    create: async (data: any) => {
        const response = await api.post('/memberships/', data);
        return response.data;
    },
    update: async (id: number, data: any) => {
        const response = await api.put(`/memberships/${id}`, data);
        return response.data;
    },
    delete: async (id: number) => {
        const response = await api.delete(`/memberships/${id}`);
        return response.data;
    }
};

export const membershipPlansApi = {
    getAll: async () => {
        const response = await api.get('/membership-plans/');
        return response.data;
    },
    create: async (data: any) => {
        const response = await api.post('/membership-plans/', data);
        return response.data;
    },
    update: async (id: number, data: any) => {
        const response = await api.put(`/membership-plans/${id}`, data);
        return response.data;
    },
    delete: async (id: number) => {
        const response = await api.delete(`/membership-plans/${id}`);
        return response.data;
    }
};

export const dashboardApi = {
    getMetrics: async () => {
        const response = await api.get('/dashboard/metrics');
        return response.data;
    },
    getAlerts: async () => {
        const response = await api.get('/dashboard/alerts');
        return response.data;
    }
};

export const programsApi = {
    getAll: async () => {
        const response = await api.get('/programs/');
        return response.data;
    },
    create: async (data: any) => {
        const response = await api.post('/programs/', data);
        return response.data;
    },
    update: async (id: number, data: any) => {
        const response = await api.put(`/programs/${id}`, data);
        return response.data;
    },
    delete: async (id: number) => {
        const response = await api.delete(`/programs/${id}`);
        return response.data;
    }
};

export interface Appointment {
    id: number;
    patient_id: number;
    appointment_date: string;
    notes?: string;
    status: string;
    created_at: string;
}

export const appointmentsApi = {
    getAll: async () => {
        const response = await api.get<Appointment[]>('/appointments/');
        return response.data;
    },
    getPatientAppointments: async (patientId: number) => {
        const response = await api.get<Appointment[]>(`/appointments/patient/${patientId}`);
        return response.data;
    },
    create: async (data: any) => {
        const response = await api.post<Appointment>('/appointments/', data);
        return response.data;
    },
    update: async (id: number, data: any) => {
        const response = await api.put<Appointment>(`/appointments/${id}`, data);
        return response.data;
    },
    delete: async (id: number) => {
        const response = await api.delete(`/appointments/${id}`);
        return response.data;
    },
    complete: async (id: number, notes: string) => {
        const response = await api.post<Appointment>(`/appointments/${id}/complete?notes=${encodeURIComponent(notes)}`);
        return response.data;
    }
};

export const authApi = {
    updateProfile: async (data: any) => {
        const response = await api.put('/auth/me', data);
        return response.data;
    }
};

export const settingsApi = {
    getSystemSettings: async () => {
        const response = await api.get('/settings/');
        return response.data;
    },
    updateSystemSettings: async (data: any) => {
        const response = await api.put('/settings/', data);
        return response.data;
    }
};

export default api;
