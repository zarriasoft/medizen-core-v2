import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi, patientApi } from '../services/api';

interface Patient {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    phone?: string;
}

interface AuthContextType {
    patient: Patient | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (e: string, p: string) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType>(null!);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [patient, setPatient] = useState<Patient | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const initAuth = async () => {
            const token = localStorage.getItem('patient_token');
            if (token) {
                try {
                    const res = await patientApi.getProfile();
                    setPatient(res.data);
                } catch (error) {
                    console.error("Failed to load profile", error);
                    localStorage.removeItem('patient_token');
                }
            }
            setIsLoading(false);
        };
        initAuth();
    }, []);

    const login = async (email: string, pass: string) => {
        const { access_token } = await authApi.login(email, pass);
        localStorage.setItem('patient_token', access_token);
        const res = await patientApi.getProfile();
        setPatient(res.data);
    };

    const logout = () => {
        localStorage.removeItem('patient_token');
        setPatient(null);
    };

    return (
        <AuthContext.Provider value={{
            patient,
            isAuthenticated: !!patient,
            isLoading,
            login,
            logout
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
