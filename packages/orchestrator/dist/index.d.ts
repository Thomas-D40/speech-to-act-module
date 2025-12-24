/**
 * Pipeline Orchestrator - REST API
 *
 * Chains the full pipeline:
 *   CanonicalFacts + Targets -> Deterministic Mapping -> Intent Gateway -> Backend
 *
 * Endpoints:
 *   POST /api/process          - Process facts through the full pipeline
 *   POST /api/process/confirm  - Confirm a pending intent
 *   POST /api/process/reject   - Reject a pending intent
 *   GET  /health               - Health check
 */
export {};
//# sourceMappingURL=index.d.ts.map