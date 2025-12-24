"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.mapDiaperFacts = mapDiaperFacts;
const types_1 = require("../types");
function mapDiaperFacts(facts) {
    const diaperFact = facts.find((f) => f.dimension === types_1.DIMENSIONS.DIAPER_CHANGE_TYPE);
    if (!diaperFact)
        return null;
    return {
        domain: types_1.DOMAINS.DIAPER,
        type: types_1.INTENTION_TYPES.DIAPER_CHANGE,
        attributes: { changeType: diaperFact.value },
        confidence: diaperFact.confidence,
    };
}
//# sourceMappingURL=diaper.js.map