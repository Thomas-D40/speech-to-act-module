"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.mapMealFacts = mapMealFacts;
const types_1 = require("../types");
const MEAL_DIMENSIONS = [
    types_1.DIMENSIONS.MEAL_MAIN_CONSUMPTION,
    types_1.DIMENSIONS.MEAL_DESSERT_CONSUMPTION,
    types_1.DIMENSIONS.MEAL_VEGETABLE_CONSUMPTION,
    types_1.DIMENSIONS.MEAL_TYPE,
];
function mapMealFacts(facts) {
    const mealFacts = facts.filter((f) => MEAL_DIMENSIONS.includes(f.dimension));
    if (mealFacts.length === 0)
        return null;
    const attributes = {};
    let totalConfidence = 0;
    for (const fact of mealFacts) {
        switch (fact.dimension) {
            case types_1.DIMENSIONS.MEAL_MAIN_CONSUMPTION:
                attributes.main = fact.value;
                break;
            case types_1.DIMENSIONS.MEAL_DESSERT_CONSUMPTION:
                attributes.dessert = fact.value;
                break;
            case types_1.DIMENSIONS.MEAL_VEGETABLE_CONSUMPTION:
                attributes.vegetable = fact.value;
                break;
            case types_1.DIMENSIONS.MEAL_TYPE:
                attributes.mealType = fact.value;
                break;
        }
        totalConfidence += fact.confidence;
    }
    return {
        domain: types_1.DOMAINS.MEAL,
        type: types_1.INTENTION_TYPES.MEAL_CONSUMPTION,
        attributes,
        confidence: totalConfidence / mealFacts.length,
    };
}
//# sourceMappingURL=meal.js.map