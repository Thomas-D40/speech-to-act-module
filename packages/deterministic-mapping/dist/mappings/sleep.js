"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.mapSleepFacts = mapSleepFacts;
const types_1 = require("../types");
function mapSleepFacts(facts) {
    const sleepFact = facts.find((f) => f.dimension === types_1.DIMENSIONS.SLEEP_STATE);
    if (!sleepFact)
        return null;
    return {
        domain: types_1.DOMAINS.SLEEP,
        type: types_1.INTENTION_TYPES.SLEEP_LOG,
        attributes: { state: sleepFact.value },
        confidence: sleepFact.confidence,
    };
}
//# sourceMappingURL=sleep.js.map