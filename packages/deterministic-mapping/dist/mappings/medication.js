"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.mapMedicationFacts = mapMedicationFacts;
const types_1 = require("../types");
function mapMedicationFacts(facts) {
    const medicationFact = facts.find((f) => f.dimension === types_1.DIMENSIONS.MEDICATION_TYPE);
    if (!medicationFact)
        return null;
    return {
        domain: types_1.DOMAINS.MEDICATION,
        type: types_1.INTENTION_TYPES.MEDICATION_ADMINISTRATION,
        attributes: { medicationType: medicationFact.value },
        confidence: medicationFact.confidence,
    };
}
//# sourceMappingURL=medication.js.map