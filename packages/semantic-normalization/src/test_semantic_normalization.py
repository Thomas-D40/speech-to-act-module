
import os
import sys
import pytest
from typing import List, Dict

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "semantic_normalization"))

from semantic_normalization.normalizer import SemanticNormalizer
from semantic_normalization.rag_interface import VectorRAGRetriever
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test Structure: Each group targets a specific WHO + WHAT + HOW
TEST_CASES = [
    {
        "description": "Gabriel ate everything",
        "phrases": [
            "Gabriel a tout mangé",
            "Gabriel a fini son assiette",
            "L'assiette de Gabriel est vide"
        ],
        "expected": {
            "subjects": ["Gabriel"],
            "dimension": "MEAL_MAIN_CONSUMPTION",
            "value": "ALL"
        }
    },
    {
        "description": "Léa is asleep",
        "phrases": [
            "Léa s'est endormie",
            "Léa fait dodo",
            "Léa est partie pour sa nuit"
        ],
        "expected": {
            "subjects": ["Léa"],
            "dimension": "SLEEP_STATE",
            "value": "ASLEEP"
        }
    },
    {
        "description": "Tom has a dirty diaper",
        "phrases": [
            "J'ai changé la couche de Tom, il y avait du caca",
            "Tom a fait une selle",
            "Gros caca pour Tom"
        ],
        "expected": {
            "subjects": ["Tom"],
            "dimension": "DIAPER_CHANGE_TYPE",
            "value": "DIRTY"
        }
    },
    {
        "description": "Pronoun 'Il' ate everything",
        "phrases": [
            "Il n'a rien laissé dans son assiette",
            "Il a tout dévoré"
        ],
        "expected": {
            "subjects": ["Il"],
            "dimension": "MEAL_MAIN_CONSUMPTION",
            "value": "ALL"
        }
    }
]

def run_tests():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ SKIPPING: OPENAI_API_KEY not found in environment variables.")
        return

    print("Starting End-to-End Semantic Normalization Tests (LLM + RAG)...")
    
    rag = VectorRAGRetriever()
    normalizer = SemanticNormalizer(api_key=api_key, rag_retriever=rag)
    
    total_tests = 0
    passed_tests = 0
    
    for group in TEST_CASES:
        expected = group["expected"]
        print(f"\n[TEST GROUP]: {group['description']}")
        print(f"   Expected: [{', '.join(expected['subjects'])}] {expected['dimension']} -> {expected['value']}")
        
        for phrase in group["phrases"]:
            total_tests += 1
            print(f"   Input: '{phrase}'")
            try:
                result = normalizer.normalize(phrase)
                
                if not result.facts:
                    print(f"    FAIL: No facts returned.")
                    continue
                
                fact = result.facts[0]
                
                # Verify Tuple (Subject, Dimension, Value)
                matches_dim = fact.dimension == expected['dimension']
                matches_val = fact.value == expected['value']
                
                # Subject Check (Case Insensitive)
                found_subjects = {s.lower() for s in fact.subjects}
                expected_subjects_set = {s.lower() for s in expected['subjects']}
                
                if "unknown" in expected_subjects_set:
                     matches_subjects = "unknown" in found_subjects
                else:
                    # Pass if at least one expected name is present (handles "Tom, il" vs "Tom")
                    matches_subjects = not found_subjects.isdisjoint(expected_subjects_set)

                if matches_dim and matches_val and matches_subjects:
                    print(f"    PASS")
                    passed_tests += 1
                else:
                    print(f"    FAIL: Got [{', '.join(fact.subjects)}] {fact.dimension} -> {fact.value}")
                    
            except Exception as e:
                print(f"    ERROR: {e}")

    print(f"\nResults: {passed_tests}/{total_tests} passed.")

if __name__ == "__main__":
    run_tests()
