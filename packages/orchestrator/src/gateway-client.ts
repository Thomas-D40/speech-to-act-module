/**
 * Client for communicating with the Intent Gateway
 */

import { GatewayPreviewResponse, GatewayCommitResponse } from './types.js';

const DEFAULT_GATEWAY_URL = 'http://localhost:3002';

export class GatewayClient {
  private readonly baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || process.env.GATEWAY_URL || DEFAULT_GATEWAY_URL;
  }

  async preview(contract: unknown): Promise<GatewayPreviewResponse> {
    const response = await fetch(`${this.baseUrl}/api/intents/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(contract),
    });

    return response.json() as Promise<GatewayPreviewResponse>;
  }

  async commit(contract: unknown): Promise<GatewayCommitResponse> {
    const response = await fetch(`${this.baseUrl}/api/intents/commit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(contract),
    });

    return response.json() as Promise<GatewayCommitResponse>;
  }

  async confirm(pendingId: string): Promise<GatewayCommitResponse> {
    const response = await fetch(`${this.baseUrl}/api/intents/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pending_id: pendingId }),
    });

    return response.json() as Promise<GatewayCommitResponse>;
  }

  async reject(pendingId: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/intents/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pending_id: pendingId }),
    });

    return response.json();
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}
