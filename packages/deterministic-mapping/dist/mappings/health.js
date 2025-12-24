"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.mapHealthFacts = mapHealthFacts;
const types_1 = require("../types");
function mapHealthFacts(facts) {
    const healthFact = facts.find((f) => f.dimension === types_1.DIMENSIONS.HEALTH_STATUS);
    if (!healthFact)
        return null;
    return {
        domain: types_1.DOMAINS.HEALTH,
        type: types_1.INTENTION_TYPES.HEALTH_OBSERVATION,
        attributes: { status: healthFact.value },
        confidence: healthFact.confidence,
    };
}
//# sourceMappingURL=health.js.map