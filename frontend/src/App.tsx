import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Login from './pages/Login';
import { AuthProvider, useAuth } from './context/AuthContext';
import Dashboard from './pages/Dashboard';
import Patients from './pages/Patients';
import PatientDetail from './pages/PatientDetail';
import Memberships from './pages/Memberships';
import Programs from './pages/Programs';
import Appointments from './pages/Appointments';
import IEIM from './pages/IEIM';
import Settings from './pages/Settings';
import Capture from './pages/Capture';

import { Toaster } from 'react-hot-toast';

const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
    const { user, isLoading } = useAuth();
    if (isLoading) {
        return <div className="h-screen w-screen flex items-center justify-center bg-slate-50"><div className="w-8 h-8 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" /></div>;
    }
    return user ? <>{children}</> : <Navigate to="/login" />;
};

function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Toaster position="top-right" toastOptions={{
                    duration: 4000,
                    style: {
                        background: '#fff',
                        color: '#334155',
                        boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
                        borderRadius: '0.75rem',
                        padding: '16px',
                        border: '1px solid #f1f5f9'
                    },
                    success: {
                        iconTheme: {
                            primary: '#0d9488',
                            secondary: '#fff',
                        },
                    },
                }} />
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/test" element={<Capture />} />
                    <Route path="/" element={
                        <PrivateRoute>
                            <Layout />
                        </PrivateRoute>
                    }>
                        <Route index element={<Dashboard />} />
                        <Route path="patients" element={<Patients />} />
                        <Route path="patients/:id" element={<PatientDetail />} />
                        {/* Future Routes */}
                        <Route path="memberships" element={<Memberships />} />
                        <Route path="programs" element={<Programs />} />
                        <Route path="calendar" element={<Appointments />} />
                        <Route path="ieim" element={<IEIM />} />
                        <Route path="settings" element={<Settings />} />
                    </Route>
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
}

export default App;
