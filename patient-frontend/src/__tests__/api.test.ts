import { describe, it, expect, beforeEach } from 'vitest';

describe('Patient API service', () => {
    beforeEach(() => {
        vi.resetModules();
        localStorage.clear();
    });

    it('uses default API URL when env var is not set', async () => {
        vi.stubEnv('VITE_API_URL', undefined as any);
        const { default: api } = await import('../services/api');
        expect(api.defaults.baseURL).toBe('http://localhost:8000');
    });

    it('attaches Authorization header when patient_token exists', async () => {
        localStorage.setItem('patient_token', 'patient-jwt');
        const { default: api } = await import('../services/api');

        const config = { headers: {} } as any;
        const handler = (api.interceptors.request as any).handlers[0];

        const result = handler.fulfilled(config);
        expect(result.headers.Authorization).toBe('Bearer patient-jwt');
    });

    it('does not attach Authorization when no patient_token', async () => {
        const { default: api } = await import('../services/api');

        const config = { headers: {} } as any;
        const handler = (api.interceptors.request as any).handlers[0];

        const result = handler.fulfilled(config);
        expect(result.headers.Authorization).toBeUndefined();
    });
});
