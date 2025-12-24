"""
CLI for testing semantic normalization
"""

import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from .normalizer import SemanticNormalizer


def main():
    """Main CLI entry point"""
    # Load environment variables
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: python -m semantic_normalization.cli \"<text to normalize>\"")
        print("Example: python -m semantic_normalization.cli \"il a mangé la moitié\"")
        sys.exit(1)

    input_text = " ".join(sys.argv[1:])

    # Initialize normalizer
    normalizer = SemanticNormalizer()

    # Normalize
    print(f"Input: {input_text}")
    print("-" * 50)

    try:
        result = normalizer.normalize(input_text)
        print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
