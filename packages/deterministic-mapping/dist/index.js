"use strict";
/**
 * Deterministic Mapping Layer
 * Pure TypeScript (NO AI/LLM) - transforms CanonicalFacts into IntentionContracts
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.INTENTION_TYPES = exports.DIMENSIONS = exports.DOMAINS = exports.DeterministicMapper = void 0;
var mapper_1 = require("./mapper");
Object.defineProperty(exports, "DeterministicMapper", { enumerable: true, get: function () { return mapper_1.DeterministicMapper; } });
var types_1 = require("./types");
Object.defineProperty(exports, "DOMAINS", { enumerable: true, get: function () { return types_1.DOMAINS; } });
Object.defineProperty(exports, "DIMENSIONS", { enumerable: true, get: function () { return types_1.DIMENSIONS; } });
Object.defineProperty(exports, "INTENTION_TYPES", { enumerable: true, get: function () { return types_1.INTENTION_TYPES; } });
__exportStar(require("./mappings"), exports);
//# sourceMappingURL=index.js.map