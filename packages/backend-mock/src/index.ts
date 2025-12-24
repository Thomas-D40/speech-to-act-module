import express, { Request, Response } from 'express';
import cors from 'cors';
import { IntentionContract, PreviewResponse, CommitResponse, AffectedEntity, DOMAINS } from './types';
import { validateIntentionContract } from './validators';

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

app.use((req, _, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

/**
 * POST /api/intents/preview - Dry-run preview of intention
 */
app.post('/api/intents/preview', (req: Request, res: Response) => {
  const validation = validateIntentionContract(req.body);

  if (!validation.isValid) {
    const response: PreviewResponse = {
      success: false,
      preview: { affectedEntities: [], description: 'Validation failed' },
      errors: validation.errors,
    };
    return res.status(400).json(response);
  }

  const contract: IntentionContract = req.body;
  const preview = generatePreview(contract);

  const response: PreviewResponse = { success: true, preview };
  res.json(response);
});

/**
 * POST /api/intents/commit - Mock commit (no persistence)
 */
app.post('/api/intents/commit', (req: Request, res: Response) => {
  const validation = validateIntentionContract(req.body);

  if (!validation.isValid) {
    const response: CommitResponse = {
      success: false,
      message: 'Validation failed',
      errors: validation.errors,
    };
    return res.status(400).json(response);
  }

  const contract: IntentionContract = req.body;
  const mockId = `mock-${Date.now()}-${Math.random().toString(36).substring(7)}`;

  const response: CommitResponse = {
    success: true,
    message: `Mock commit successful for ${contract.targets.join(', ')} - ${contract.domain}/${contract.type}`,
    mockId,
    timestamp: new Date().toISOString(),
  };

  res.json(response);
});

app.get('/health', (_, res: Response) => {
  res.json({ status: 'ok', service: 'backend-mock', timestamp: new Date().toISOString() });
});

app.get('/', (_, res: Response) => {
  res.json({
    service: 'Speech-to-Act Mock Backend API',
    version: '1.0.0',
    endpoints: {
      preview: 'POST /api/intents/preview',
      commit: 'POST /api/intents/commit',
      health: 'GET /health',
    },
  });
});

function generatePreview(contract: IntentionContract): {
  affectedEntities: AffectedEntity[];
  description: string;
  warnings?: string[];
} {
  const warnings: string[] = [];

  const entity: AffectedEntity = {
    entityType: getEntityType(contract.domain),
    targets: contract.targets,
    operation: 'CREATE',
    changes: {
      ...contract.attributes,
      timestamp: contract.metadata?.timestamp || new Date().toISOString(),
    },
  };

  const description = `Would create ${entity.entityType} for ${contract.targets.join(', ')}`;

  if (contract.metadata?.confidence && contract.metadata.confidence < 0.7) {
    warnings.push('Low confidence score - consider manual verification');
  }

  if (contract.domain === DOMAINS.MEDICATION) {
    warnings.push('Medication administration requires verification');
  }

  return {
    affectedEntities: [entity],
    description,
    ...(warnings.length > 0 && { warnings }),
  };
}

function getEntityType(domain: string): string {
  const mapping: Record<string, string> = {
    MEAL: 'MealRecord',
    SLEEP: 'SleepRecord',
    DIAPER: 'DiaperChangeRecord',
    ACTIVITY: 'ActivityRecord',
    HEALTH: 'HealthObservation',
    BEHAVIOR: 'BehaviorLog',
    MEDICATION: 'MedicationRecord',
  };
  return mapping[domain] || 'Record';
}

app.listen(PORT, () => {
  console.log('='.repeat(50));
  console.log('Speech-to-Act Mock Backend API');
  console.log(`Server running on http://localhost:${PORT}`);
  console.log('NOTE: This is a MOCK server - no data is persisted');
  console.log('='.repeat(50));
});
