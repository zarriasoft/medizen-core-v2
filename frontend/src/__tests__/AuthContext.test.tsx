import { renderHook, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '../context/AuthContext';
import api from '../services/api';
import { vi, describe, it, expect, beforeEach } from 'vitest';

vi.mock('../services/api', () => ({
    default: {
        get: vi.fn(),
    },
}));

describe('AuthContext', () => {
    beforeEach(() => {
        localStorage.clear();
        vi.clearAllMocks();
    });

    const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
    );

    it('initial state has user null and resolves loading', async () => {
        const { result } = renderHook(() => useAuth(), { wrapper });
        expect(result.current.user).toBeNull();
        expect(result.current.token).toBeNull();
        await vi.waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });
    });

    it('login sets user and token in localStorage', () => {
        const { result } = renderHook(() => useAuth(), { wrapper });

        const mockUser = { username: 'admin', email: 'admin@test.com', full_name: 'Admin', role: 'admin', is_active: true };

        act(() => {
            result.current.login('fake-token', mockUser);
        });

        expect(result.current.user).toEqual(mockUser);
        expect(result.current.token).toBe('fake-token');
        expect(localStorage.getItem('token')).toBe('fake-token');
    });

    it('logout clears user and token', () => {
        const { result } = renderHook(() => useAuth(), { wrapper });

        act(() => {
            result.current.login('token-123', { username: 'admin', email: 'a@b.com', full_name: 'A', role: 'admin', is_active: true });
        });

        act(() => {
            result.current.logout();
        });

        expect(result.current.user).toBeNull();
        expect(result.current.token).toBeNull();
        expect(localStorage.getItem('token')).toBeNull();
    });

    it('validates token on mount and sets user', async () => {
        localStorage.setItem('token', 'existing-token');
        const mockUser = { username: 'doctor', email: 'doc@test.com', full_name: 'Doctor', role: 'doctor', is_active: true };
        vi.mocked(api.get).mockResolvedValueOnce({ data: mockUser });

        const { result } = renderHook(() => useAuth(), { wrapper });

        await vi.waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.user).toEqual(mockUser);
        expect(result.current.token).toBe('existing-token');
        expect(api.get).toHaveBeenCalledWith('/auth/me');
    });

    it('logs out if token validation fails', async () => {
        localStorage.setItem('token', 'bad-token');
        vi.mocked(api.get).mockRejectedValueOnce(new Error('Unauthorized'));

        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

        const { result } = renderHook(() => useAuth(), { wrapper });

        await vi.waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.user).toBeNull();
        expect(result.current.token).toBeNull();
        expect(localStorage.getItem('token')).toBeNull();

        consoleSpy.mockRestore();
    });
});
