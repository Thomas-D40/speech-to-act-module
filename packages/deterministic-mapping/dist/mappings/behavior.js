"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.mapBehaviorFacts = mapBehaviorFacts;
const types_1 = require("../types");
function mapBehaviorFacts(facts) {
    const moodFact = facts.find((f) => f.dimension === types_1.DIMENSIONS.CHILD_MOOD);
    if (!moodFact)
        return null;
    return {
        domain: types_1.DOMAINS.BEHAVIOR,
        type: types_1.INTENTION_TYPES.BEHAVIOR_LOG,
        attributes: { mood: moodFact.value },
        confidence: moodFact.confidence,
    };
}
//# sourceMappingURL=behavior.js.map