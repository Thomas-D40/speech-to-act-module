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

import express, { Request, Response } from 'express';
import cors from 'cors';
import { validateIntentionContract } from './validator.js';
import { BackendClient } from './backend-client.js';
import { pendingStore } from './pending-store.js';
import { IntentionContract } from './types.js';

const app = express();
const PORT = process.env.GATEWAY_PORT || 3002;
const backendClient = new BackendClient();

app.use(cors());
app.use(express.json());

// Logging middleware
app.use((req, _, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

/**
 * POST /api/intents/preview
 * Validate and preview an intention contract, store as pending
 */
app.post('/api/intents/preview', async (req: Request, res: Response) => {
  const contract = req.body as IntentionContract;

  // Local validation
  const validation = validateIntentionContract(contract);
  if (!validation.isValid) {
    return res.status(400).json({
      success: false,
      stage: 'local_validation',
      errors: validation.errors,
    });
  }

  // Call backend preview
  try {
    const response = await backendClient.preview(contract);

    if (!response.success) {
      return res.status(400).json({
        success: false,
        stage: 'backend_preview',
        errors: response.errors,
      });
    }

    // Store as pending
    const pending = pendingStore.add(contract, response.preview);

    res.json({
      success: true,
      stage: 'pending_confirmation',
      pending_id: pending.id,
      expires_at: pending.expiresAt.toISOString(),
      preview: response.preview,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    res.status(503).json({
      success: false,
      stage: 'backend_connection',
      error: `Failed to connect to backend: ${message}`,
    });
  }
});

/**
 * GET /api/intents/pending
 * List all pending intents awaiting confirmation
 */
app.get('/api/intents/pending', (_: Request, res: Response) => {
  const pendingList = pendingStore.list();

  const formatted = pendingList.map((p) => ({
    pending_id: p.id,
    domain: p.contract.domain,
    type: p.contract.type,
    targets: p.contract.targets,
    description: p.preview.description,
    warnings: p.preview.warnings,
    created_at: p.createdAt.toISOString(),
    expires_at: p.expiresAt.toISOString(),
  }));

  res.json({
    count: pendingList.length,
    pending: formatted,
  });
});

/**
 * POST /api/intents/confirm
 * Confirm and commit a pending intent by ID
 */
app.post('/api/intents/confirm', async (req: Request, res: Response) => {
  const { pending_id } = req.body;

  if (!pending_id) {
    return res.status(400).json({
      success: false,
      error: 'pending_id is required',
    });
  }

  const pending = pendingStore.get(pending_id);

  if (!pending) {
    return res.status(404).json({
      success: false,
      error: 'Pending intent not found or expired',
    });
  }

  try {
    const response = await backendClient.commit(pending.contract);

    if (!response.success) {
      return res.status(400).json({
        success: false,
        stage: 'backend_commit',
        errors: response.errors,
      });
    }

    pendingStore.remove(pending_id);

    res.json({
      success: true,
      stage: 'committed',
      message: response.message,
      mock_id: response.mockId,
      timestamp: response.timestamp,
      contract: {
        domain: pending.contract.domain,
        type: pending.contract.type,
        targets: pending.contract.targets,
      },
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    res.status(503).json({
      success: false,
      stage: 'backend_connection',
      error: `Failed to connect to backend: ${message}`,
    });
  }
});

/**
 * POST /api/intents/reject
 * Reject a pending intent without committing
 */
app.post('/api/intents/reject', (req: Request, res: Response) => {
  const { pending_id } = req.body;

  if (!pending_id) {
    return res.status(400).json({
      success: false,
      error: 'pending_id is required',
    });
  }

  const pending = pendingStore.get(pending_id);

  if (!pending) {
    return res.status(404).json({
      success: false,
      error: 'Pending intent not found or expired',
    });
  }

  pendingStore.remove(pending_id);

  res.json({
    success: true,
    message: 'Intent rejected and removed',
    rejected: {
      domain: pending.contract.domain,
      type: pending.contract.type,
      targets: pending.contract.targets,
    },
  });
});

/**
 * POST /api/intents/commit
 * Direct commit without confirmation (trusted workflow)
 */
app.post('/api/intents/commit', async (req: Request, res: Response) => {
  const contract = req.body as IntentionContract;

  // Local validation
  const validation = validateIntentionContract(contract);
  if (!validation.isValid) {
    return res.status(400).json({
      success: false,
      stage: 'local_validation',
      errors: validation.errors,
    });
  }

  try {
    const response = await backendClient.commit(contract);

    if (!response.success) {
      return res.status(400).json({
        success: false,
        stage: 'backend_commit',
        errors: response.errors,
      });
    }

    res.json({
      success: true,
      stage: 'committed',
      message: response.message,
      mock_id: response.mockId,
      timestamp: response.timestamp,
      contract: {
        domain: contract.domain,
        type: contract.type,
        targets: contract.targets,
      },
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    res.status(503).json({
      success: false,
      stage: 'backend_connection',
      error: `Failed to connect to backend: ${message}`,
    });
  }
});

/**
 * GET /health
 * Health check endpoint
 */
app.get('/health', async (_: Request, res: Response) => {
  const backendHealthy = await backendClient.healthCheck();

  res.json({
    status: 'ok',
    service: 'intent-gateway',
    backend_available: backendHealthy,
    backend_url: process.env.BACKEND_URL || 'http://localhost:3001',
    timestamp: new Date().toISOString(),
  });
});

/**
 * GET /
 * Service info
 */
app.get('/', (_: Request, res: Response) => {
  res.json({
    service: 'Speech-to-Act Intent Gateway',
    version: '1.0.0',
    endpoints: {
      preview: 'POST /api/intents/preview',
      pending: 'GET /api/intents/pending',
      confirm: 'POST /api/intents/confirm',
      reject: 'POST /api/intents/reject',
      commit: 'POST /api/intents/commit',
      health: 'GET /health',
    },
  });
});

app.listen(PORT, () => {
  console.log('='.repeat(50));
  console.log('Speech-to-Act Intent Gateway');
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Backend URL: ${process.env.BACKEND_URL || 'http://localhost:3001'}`);
  console.log('='.repeat(50));
});
