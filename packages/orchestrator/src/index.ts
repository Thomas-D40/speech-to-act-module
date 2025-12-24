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

import express, { Request, Response } from 'express';
import cors from 'cors';
import {
  DeterministicMapper,
  CanonicalFact,
  MappingInput,
} from '@speech-to-act/deterministic-mapping';
import { GatewayClient } from './gateway-client.js';
import { ProcessRequest } from './types.js';

const app = express();
const PORT = process.env.ORCHESTRATOR_PORT || 3003;
const mapper = new DeterministicMapper();
const gatewayClient = new GatewayClient();

app.use(cors());
app.use(express.json());

// Logging middleware
app.use((req, _, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

/**
 * POST /api/process
 * Process canonical facts through the full pipeline
 *
 * Body:
 *   - facts: Array of CanonicalFact
 *   - targets: Array of child names
 *   - workflow: 'safe' (preview+confirm) or 'fast' (direct commit)
 */
app.post('/api/process', async (req: Request, res: Response) => {
  const { facts, targets, workflow = 'safe' } = req.body as ProcessRequest;

  // Validate input
  if (!facts || !Array.isArray(facts) || facts.length === 0) {
    return res.status(400).json({
      success: false,
      stage: 'input_validation',
      error: 'facts array is required and must not be empty',
    });
  }

  if (!targets || !Array.isArray(targets) || targets.length === 0) {
    return res.status(400).json({
      success: false,
      stage: 'input_validation',
      error: 'targets array is required and must not be empty',
    });
  }

  // Step 1: Deterministic Mapping
  let intentionContract;
  try {
    const mappingInput: MappingInput = {
      facts: facts as CanonicalFact[],
      targets,
    };

    // Validate facts
    if (!mapper.validateFacts(mappingInput.facts)) {
      return res.status(400).json({
        success: false,
        stage: 'mapping_validation',
        error: 'Invalid facts: each fact must have dimension, value, and confidence (0-1)',
      });
    }

    intentionContract = mapper.map(mappingInput);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return res.status(400).json({
      success: false,
      stage: 'mapping',
      error: `Mapping failed: ${message}`,
    });
  }

  // Step 2: Call Intent Gateway
  try {
    if (workflow === 'fast') {
      // Direct commit
      const response = await gatewayClient.commit(intentionContract);

      if (!response.success) {
        return res.status(400).json({
          success: false,
          stage: response.stage || 'gateway_commit',
          errors: response.errors,
          error: response.error,
        });
      }

      return res.json({
        success: true,
        stage: 'committed',
        workflow: 'fast',
        intention_contract: {
          domain: intentionContract.domain,
          type: intentionContract.type,
          targets: intentionContract.targets,
          attributes: intentionContract.attributes,
        },
        committed: {
          mock_id: response.mock_id,
          timestamp: response.timestamp,
          message: response.message,
        },
      });
    } else {
      // Safe workflow: preview first
      const response = await gatewayClient.preview(intentionContract);

      if (!response.success) {
        return res.status(400).json({
          success: false,
          stage: response.stage || 'gateway_preview',
          errors: response.errors,
          error: response.error,
        });
      }

      return res.json({
        success: true,
        stage: 'pending_confirmation',
        workflow: 'safe',
        intention_contract: {
          domain: intentionContract.domain,
          type: intentionContract.type,
          targets: intentionContract.targets,
          attributes: intentionContract.attributes,
        },
        pending_id: response.pending_id,
        expires_at: response.expires_at,
        preview: response.preview,
      });
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return res.status(503).json({
      success: false,
      stage: 'gateway_connection',
      error: `Failed to connect to intent gateway: ${message}`,
    });
  }
});

/**
 * POST /api/process/confirm
 * Confirm a pending intent
 */
app.post('/api/process/confirm', async (req: Request, res: Response) => {
  const { pending_id } = req.body;

  if (!pending_id) {
    return res.status(400).json({
      success: false,
      error: 'pending_id is required',
    });
  }

  try {
    const response = await gatewayClient.confirm(pending_id);

    if (!response.success) {
      return res.status(400).json({
        success: false,
        stage: response.stage || 'gateway_confirm',
        errors: response.errors,
        error: response.error,
      });
    }

    res.json({
      success: true,
      stage: 'committed',
      message: response.message,
      mock_id: response.mock_id,
      timestamp: response.timestamp,
      contract: response.contract,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    res.status(503).json({
      success: false,
      stage: 'gateway_connection',
      error: `Failed to connect to intent gateway: ${message}`,
    });
  }
});

/**
 * POST /api/process/reject
 * Reject a pending intent
 */
app.post('/api/process/reject', async (req: Request, res: Response) => {
  const { pending_id } = req.body;

  if (!pending_id) {
    return res.status(400).json({
      success: false,
      error: 'pending_id is required',
    });
  }

  try {
    const response = await gatewayClient.reject(pending_id);

    if (!response.success) {
      return res.status(400).json({
        success: false,
        error: 'Failed to reject intent',
      });
    }

    res.json({
      success: true,
      message: response.message,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    res.status(503).json({
      success: false,
      stage: 'gateway_connection',
      error: `Failed to connect to intent gateway: ${message}`,
    });
  }
});

/**
 * GET /health
 * Health check endpoint
 */
app.get('/health', async (_: Request, res: Response) => {
  const gatewayHealthy = await gatewayClient.healthCheck();

  res.json({
    status: 'ok',
    service: 'orchestrator',
    gateway_available: gatewayHealthy,
    gateway_url: process.env.GATEWAY_URL || 'http://localhost:3002',
    timestamp: new Date().toISOString(),
  });
});

/**
 * GET /
 * Service info
 */
app.get('/', (_: Request, res: Response) => {
  res.json({
    service: 'Speech-to-Act Pipeline Orchestrator',
    version: '1.0.0',
    description: 'Chains: CanonicalFacts -> Mapping -> Gateway -> Backend',
    endpoints: {
      process: 'POST /api/process',
      confirm: 'POST /api/process/confirm',
      reject: 'POST /api/process/reject',
      health: 'GET /health',
    },
  });
});

app.listen(PORT, () => {
  console.log('='.repeat(50));
  console.log('Speech-to-Act Pipeline Orchestrator');
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Gateway URL: ${process.env.GATEWAY_URL || 'http://localhost:3002'}`);
  console.log('='.repeat(50));
});
