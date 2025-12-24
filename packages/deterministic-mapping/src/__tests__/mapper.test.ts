import { DeterministicMapper } from '../mapper';
import { DIMENSIONS, DOMAINS, INTENTION_TYPES } from '../types';

describe('DeterministicMapper', () => {
  let mapper: DeterministicMapper;

  beforeEach(() => {
    mapper = new DeterministicMapper();
  });

  describe('map', () => {
    it('should map MEAL_MAIN_CONSUMPTION with target', () => {
      const result = mapper.map({
        facts: [{ dimension: DIMENSIONS.MEAL_MAIN_CONSUMPTION, value: 'HALF', confidence: 0.92 }],
        targets: ['Lucas'],
      });

      expect(result.domain).toBe(DOMAINS.MEAL);
      expect(result.type).toBe(INTENTION_TYPES.MEAL_CONSUMPTION);
      expect(result.targets).toEqual(['Lucas']);
      expect(result.attributes.main).toBe('HALF');
      expect(result.metadata?.confidence).toBe(0.92);
    });

    it('should map multiple children in targets', () => {
      const result = mapper.map({
        facts: [{ dimension: DIMENSIONS.ACTIVITY_TYPE, value: 'OUTDOOR_PLAY', confidence: 0.88 }],
        targets: ['Jules', 'Lina'],
      });

      expect(result.targets).toEqual(['Jules', 'Lina']);
      expect(result.domain).toBe(DOMAINS.ACTIVITY);
    });

    it('should throw error for empty facts', () => {
      expect(() => mapper.map({ facts: [], targets: ['Paul'] })).toThrow('Cannot map empty facts array');
    });

    it('should throw error for empty targets', () => {
      expect(() =>
        mapper.map({
          facts: [{ dimension: DIMENSIONS.SLEEP_STATE, value: 'ASLEEP', confidence: 0.9 }],
          targets: [],
        })
      ).toThrow('Cannot map without targets');
    });

    it('should be deterministic - same input produces same output', () => {
      const input = {
        facts: [{ dimension: DIMENSIONS.MEAL_MAIN_CONSUMPTION, value: 'THREE_QUARTERS', confidence: 0.88 }],
        targets: ['Nathan'],
      };

      const result1 = mapper.map(input);
      const result2 = mapper.map(input);

      expect(result1.domain).toBe(result2.domain);
      expect(result1.type).toBe(result2.type);
      expect(result1.targets).toEqual(result2.targets);
      expect(result1.attributes).toEqual(result2.attributes);
      expect(result1.metadata?.confidence).toBe(result2.metadata?.confidence);
    });
  });

  describe('validateFacts', () => {
    it('should validate valid facts', () => {
      const facts = [{ dimension: DIMENSIONS.MEAL_MAIN_CONSUMPTION, value: 'HALF', confidence: 0.92 }];
      expect(mapper.validateFacts(facts)).toBe(true);
    });

    it('should reject facts with invalid confidence', () => {
      const facts = [{ dimension: DIMENSIONS.MEAL_MAIN_CONSUMPTION, value: 'HALF', confidence: 1.5 }];
      expect(mapper.validateFacts(facts)).toBe(false);
    });
  });
});
