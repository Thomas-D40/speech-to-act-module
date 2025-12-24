/**
 * Intent Gateway - REST API
 *
 * Validates intention contracts and communicates with backend API.
 * Acts as a firewall between the orchestrator and the backend.
 *
 * Endpoints:
 *   POST /api/intents/preview  - Validate and preview, store as pending
 *   GET  /api/intents/pending  - List pending intents
 *   POST /api/intents/confirm  - Confirm and commit a pending intent
 *   POST /api/intents/reject   - Reject a pending intent
 *   POST /api/intents/commit   - Direct commit (trusted workflow)
 *   GET  /health               - Health check
 */
export {};
//# sourceMappingURL=index.d.ts.map