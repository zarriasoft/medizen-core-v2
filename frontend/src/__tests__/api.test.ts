import { describe, it, expect, beforeEach } from 'vitest';

describe('API service', () => {
    beforeEach(() => {
        vi.resetModules();
        localStorage.clear();
        vi.unstubAllEnvs();
    });

    it('uses default API URL when env var is not set', async () => {
        vi.stubEnv('VITE_API_URL', undefined as any);
        const { default: api } = await import('../services/api');
        expect(api.defaults.baseURL).toBe('http://127.0.0.1:8000');
    });

    it('attaches Authorization header when token exists', async () => {
        localStorage.setItem('token', 'test-jwt-token');
        const { default: api } = await import('../services/api');

        const config = { headers: {} } as any;
        const handler = (api.interceptors.request as any).handlers[0];

        const result = handler.fulfilled(config);
        expect(result.headers.Authorization).toBe('Bearer test-jwt-token');
    });

    it('does not attach Authorization when no token', async () => {
        const { default: api } = await import('../services/api');

        const config = { headers: {} } as any;
        const handler = (api.interceptors.request as any).handlers[0];

        const result = handler.fulfilled(config);
        expect(result.headers.Authorization).toBeUndefined();
    });
});
