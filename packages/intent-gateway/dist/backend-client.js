/**
 * Backend API client for communicating with the mock backend
 */
const DEFAULT_BACKEND_URL = 'http://localhost:3001';
export class BackendClient {
    baseUrl;
    constructor(baseUrl) {
        this.baseUrl = baseUrl || process.env.BACKEND_URL || DEFAULT_BACKEND_URL;
    }
    async preview(contract) {
        const response = await fetch(`${this.baseUrl}/api/intents/preview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(contract),
        });
        const data = await response.json();
        if (!response.ok) {
            return data;
        }
        return data;
    }
    async commit(contract) {
        const response = await fetch(`${this.baseUrl}/api/intents/commit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(contract),
        });
        const data = await response.json();
        if (!response.ok) {
            return data;
        }
        return data;
    }
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            return response.ok;
        }
        catch {
            return false;
        }
    }
}
