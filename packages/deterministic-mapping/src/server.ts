/**
 * Deterministic Mapping REST API Server
 *
 * Exposes the mapping schema for semantic-normalization to query.
 * This allows the LLM to know what dimensions and values are valid.
 *
 * Endpoints:
 *   GET /schema           - Full schema (dimensions, values, domains)
 *   GET /schema/dimensions - List of all dimensions with descriptions
 *   GET /schema/domains    - List of all domains
 *   POST /map              - Map canonical facts to intention contract
 *   GET /health            - Health check
 */

import express, { Request, Response } from 'express';
import cors from 'cors';
import { DeterministicMapper } from './mapper.js';
import {
  getSchema,
  DOMAINS,
  DIMENSIONS,
  DIMENSION_VALUES,
  DIMENSION_DESCRIPTIONS,
  DIMENSION_TO_DOMAIN,
  MappingInput,
  CanonicalFact,
} from './types.js';

const app = express();
const PORT = process.env.MAPPING_PORT || 3004;
const mapper = new DeterministicMapper();

app.use(cors());
app.use(express.json());

// Logging middleware
app.use((req, _, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

/**
 * GET /schema
 * Returns the full mapping schema for semantic-normalization
 */
app.get('/schema', (_: Request, res: Response) => {
  res.json(getSchema());
});

/**
 * GET /schema/dimensions
 * Returns all dimensions with their valid values
 */
app.get('/schema/dimensions', (_: Request, res: Response) => {
  const dimensions = Object.values(DIMENSIONS).map((dim) => ({
    dimension: dim,
    description: DIMENSION_DESCRIPTIONS[dim],
    domain: DIMENSION_TO_DOMAIN[dim],
    validValues: DIMENSION_VALUES[dim],
  }));

  res.json({ dimensions });
});

/**
 * GET /schema/domains
 * Returns all valid domains
 */
app.get('/schema/domains', (_: Request, res: Response) => {
  res.json({ domains: Object.values(DOMAINS) });
});

/**
 * GET /schema/prompt
 * Returns a formatted prompt snippet for LLM classification
 */
app.get('/schema/prompt', (_: Request, res: Response) => {
  const schema = getSchema();

  let prompt = 'You must classify the user input into one of the following dimensions:\n\n';

  for (const dim of schema.dimensions) {
    prompt += `## ${dim.dimension}\n`;
    prompt += `Description: ${dim.description}\n`;
    prompt += `Domain: ${dim.domain}\n`;
    prompt += `Valid values: ${dim.validValues.join(', ')}\n\n`;
  }

  prompt += '\nOutput format (JSON):\n';
  prompt += '{\n';
  prompt += '  "facts": [\n';
  prompt += '    {\n';
  prompt += '      "dimension": "<DIMENSION>",\n';
  prompt += '      "value": "<VALUE>",\n';
  prompt += '      "confidence": <0.0-1.0>\n';
  prompt += '    }\n';
  prompt += '  ],\n';
  prompt += '  "targets": ["<child_name>", ...]\n';
  prompt += '}\n';

  res.json({
    prompt,
    schema,
  });
});

/**
 * POST /map
 * Maps canonical facts to an intention contract
 */
app.post('/map', (req: Request, res: Response) => {
  const { facts, targets } = req.body as MappingInput;

  if (!facts || !Array.isArray(facts) || facts.length === 0) {
    return res.status(400).json({
      success: false,
      error: 'facts array is required and must not be empty',
    });
  }

  if (!targets || !Array.isArray(targets) || targets.length === 0) {
    return res.status(400).json({
      success: false,
      error: 'targets array is required and must not be empty',
    });
  }

  // Validate facts
  if (!mapper.validateFacts(facts as CanonicalFact[])) {
    return res.status(400).json({
      success: false,
      error: 'Invalid facts: each fact must have dimension, value, and confidence (0-1)',
    });
  }

  try {
    const contract = mapper.map({ facts: facts as CanonicalFact[], targets });
    res.json({
      success: true,
      intentionContract: contract,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    res.status(400).json({
      success: false,
      error: message,
    });
  }
});

/**
 * GET /health
 * Health check endpoint
 */
app.get('/health', (_: Request, res: Response) => {
  res.json({
    status: 'ok',
    service: 'deterministic-mapping',
    timestamp: new Date().toISOString(),
  });
});

/**
 * GET /
 * Service info
 */
app.get('/', (_: Request, res: Response) => {
  res.json({
    service: 'Speech-to-Act Deterministic Mapping',
    version: '1.0.0',
    description: 'Exposes schema for semantic-normalization and maps facts to contracts',
    endpoints: {
      schema: 'GET /schema',
      dimensions: 'GET /schema/dimensions',
      domains: 'GET /schema/domains',
      prompt: 'GET /schema/prompt',
      map: 'POST /map',
      health: 'GET /health',
    },
  });
});

app.listen(PORT, () => {
  console.log('='.repeat(50));
  console.log('Speech-to-Act Deterministic Mapping API');
  console.log(`Server running on http://localhost:${PORT}`);
  console.log('='.repeat(50));
});
