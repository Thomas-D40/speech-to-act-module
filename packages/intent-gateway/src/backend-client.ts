/**
 * Backend API client for communicating with the mock backend
 */

import { IntentionContract, PreviewResponse, CommitResponse } from './types.js';

const DEFAULT_BACKEND_URL = 'http://localhost:3001';

export class BackendClient {
  private readonly baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || process.env.BACKEND_URL || DEFAULT_BACKEND_URL;
  }

  async preview(contract: IntentionContract): Promise<PreviewResponse> {
    const response = await fetch(`${this.baseUrl}/api/intents/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(contract),
    });

    const data = await response.json();

    if (!response.ok) {
      return data as PreviewResponse;
    }

    return data as PreviewResponse;
  }

  async commit(contract: IntentionContract): Promise<CommitResponse> {
    const response = await fetch(`${this.baseUrl}/api/intents/commit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(contract),
    });

    const data = await response.json();

    if (!response.ok) {
      return data as CommitResponse;
    }

    return data as CommitResponse;
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
