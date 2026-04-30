import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '../context/AuthContext';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import api from '../services/api';

vi.mock('../services/api', () => ({
    default: {
        get: vi.fn(),
    },
}));

const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
    const { user, isLoading } = useAuth();
    if (isLoading) return <div>Loading...</div>;
    return user ? <>{children}</> : <Navigate to="/login" />;
};

describe('PrivateRoute', () => {
    beforeEach(() => {
        localStorage.clear();
        vi.clearAllMocks();
    });

    it('renders children when user is authenticated', async () => {
        localStorage.setItem('token', 'valid-token');
        vi.mocked(api.get).mockResolvedValueOnce({
            data: { username: 'admin', email: 'admin@test.com', full_name: 'Admin', role: 'admin', is_active: true },
        });

        render(
            <AuthProvider>
                <MemoryRouter initialEntries={['/dashboard']}>
                    <Routes>
                        <Route path="/login" element={<div>Login Page</div>} />
                        <Route
                            path="/dashboard"
                            element={
                                <PrivateRoute>
                                    <div>Dashboard Content</div>
                                </PrivateRoute>
                            }
                        />
                    </Routes>
                </MemoryRouter>
            </AuthProvider>
        );

        await vi.waitFor(() => {
            expect(screen.getByText('Dashboard Content')).toBeInTheDocument();
        });
    });

    it('redirects to /login when user is not authenticated', async () => {
        render(
            <AuthProvider>
                <MemoryRouter initialEntries={['/dashboard']}>
                    <Routes>
                        <Route path="/login" element={<div>Login Page</div>} />
                        <Route
                            path="/dashboard"
                            element={
                                <PrivateRoute>
                                    <div>Dashboard Content</div>
                                </PrivateRoute>
                            }
                        />
                    </Routes>
                </MemoryRouter>
            </AuthProvider>
        );

        await vi.waitFor(() => {
            expect(screen.getByText('Login Page')).toBeInTheDocument();
        });
    });
});
