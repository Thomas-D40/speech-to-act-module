/**
 * Deterministic Mapping Layer
 * Pure TypeScript (NO AI/LLM) - transforms CanonicalFacts into IntentionContracts
 */

export { DeterministicMapper } from './mapper';
export {
  DOMAINS,
  DIMENSIONS,
  INTENTION_TYPES,
  type Domain,
  type Dimension,
  type IntentionType,
  type IntentionContract,
  type CanonicalFact,
  type MappingResult,
  type MappingFunction,
  type MappingInput,
} from './types';
export * from './mappings';
