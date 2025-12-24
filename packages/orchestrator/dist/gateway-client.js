/**
 * Client for communicating with the Intent Gateway
 */
const DEFAULT_GATEWAY_URL = 'http://localhost:3002';
export class GatewayClient {
    baseUrl;
    constructor(baseUrl) {
        this.baseUrl = baseUrl || process.env.GATEWAY_URL || DEFAULT_GATEWAY_URL;
    }
    async preview(contract) {
        const response = await fetch(`${this.baseUrl}/api/intents/preview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(contract),
        });
        return response.json();
    }
    async commit(contract) {
        const response = await fetch(`${this.baseUrl}/api/intents/commit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(contract),
        });
        return response.json();
    }
    async confirm(pendingId) {
        const response = await fetch(`${this.baseUrl}/api/intents/confirm`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pending_id: pendingId }),
        });
        return response.json();
    }
    async reject(pendingId) {
        const response = await fetch(`${this.baseUrl}/api/intents/reject`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pending_id: pendingId }),
        });
        return response.json();
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
