"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.mapActivityFacts = mapActivityFacts;
const types_1 = require("../types");
function mapActivityFacts(facts) {
    const activityFact = facts.find((f) => f.dimension === types_1.DIMENSIONS.ACTIVITY_TYPE);
    if (!activityFact)
        return null;
    return {
        domain: types_1.DOMAINS.ACTIVITY,
        type: types_1.INTENTION_TYPES.ACTIVITY_LOG,
        attributes: { activityType: activityFact.value },
        confidence: activityFact.confidence,
    };
}
//# sourceMappingURL=activity.js.map