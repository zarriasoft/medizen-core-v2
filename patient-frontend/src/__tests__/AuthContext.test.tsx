import { renderHook, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { authApi, patientApi } from '../services/api';
import { vi, describe, it, expect, beforeEach } from 'vitest';

vi.mock('../services/api', () => ({
    authApi: { login: vi.fn() },
    patientApi: { getProfile: vi.fn() },
    default: {
        interceptors: {
            request: { use: vi.fn() },
            response: { use: vi.fn() },
        },
    },
}));

describe('AuthContext (patient)', () => {
    beforeEach(() => {
        localStorage.clear();
        vi.clearAllMocks();
    });

    const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
    );

    it('initial state has isAuthenticated false and resolves loading', async () => {
        const { result } = renderHook(() => useAuth(), { wrapper });
        expect(result.current.isAuthenticated).toBe(false);
        expect(result.current.patient).toBeNull();
        await vi.waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });
    });

    it('login authenticates patient and stores token', async () => {
        const mockPatient = { id: 1, first_name: 'Juan', last_name: 'Perez', email: 'juan@test.com' };
        vi.mocked(authApi.login).mockResolvedValueOnce({ access_token: 'patient-token-123' });
        vi.mocked(patientApi.getProfile).mockResolvedValueOnce({ data: mockPatient });

        const { result } = renderHook(() => useAuth(), { wrapper });

        await act(async () => {
            await result.current.login('juan@test.com', 'password123');
        });

        expect(result.current.patient).toEqual(mockPatient);
        expect(result.current.isAuthenticated).toBe(true);
        expect(localStorage.getItem('patient_token')).toBe('patient-token-123');
    });

    it('logout clears patient and token', () => {
        const { result } = renderHook(() => useAuth(), { wrapper });

        act(() => {
            result.current.logout();
        });

        expect(result.current.patient).toBeNull();
        expect(result.current.isAuthenticated).toBe(false);
        expect(localStorage.getItem('patient_token')).toBeNull();
    });

    it('loads profile on mount if token exists', async () => {
        localStorage.setItem('patient_token', 'existing-token');
        const mockPatient = { id: 2, first_name: 'Maria', last_name: 'Lopez', email: 'maria@test.com' };
        vi.mocked(patientApi.getProfile).mockResolvedValueOnce({ data: mockPatient });

        const { result } = renderHook(() => useAuth(), { wrapper });

        await vi.waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.patient).toEqual(mockPatient);
        expect(result.current.isAuthenticated).toBe(true);
    });

    it('clears token if profile load fails on mount', async () => {
        localStorage.setItem('patient_token', 'bad-token');
        vi.mocked(patientApi.getProfile).mockRejectedValueOnce(new Error('Failed'));
        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

        const { result } = renderHook(() => useAuth(), { wrapper });

        await vi.waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.patient).toBeNull();
        expect(result.current.isAuthenticated).toBe(false);
        expect(localStorage.getItem('patient_token')).toBeNull();

        consoleSpy.mockRestore();
    });
});
