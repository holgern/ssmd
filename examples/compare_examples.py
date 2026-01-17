#!/usr/bin/env python3
"""Example SSMD/SSML comparison script.

This script demonstrates bidirectional conversion:
1. Reads example_ssmd.md, converts to SSML, and stores it.
2. Reads example_ssml.xml, converts to SSMD, and stores it.
"""

import sys
from pathlib import Path

import ssmd


def main() -> int:
    # Determine examples directory
    examples_dir = Path(__file__).parent
    ssmd_file = examples_dir / "example_ssmd.md"
    ssmd_out_file = examples_dir / "example_ssmd_from_ssml.md"
    ssmd_returned_file = examples_dir / "example_ssmd_returned.md"
    ssml_file = examples_dir / "example_ssml.xml"
    ssml_out_file = examples_dir / "example_ssml_from_ssmd.xml"
    ssml_returned_file = examples_dir / "example_ssml_returned.xml"

    # Check if files exist
    if not ssmd_file.exists():
        print(f"Error: {ssmd_file} not found")
        return 1

    if not ssml_file.exists():
        print(f"Error: {ssml_file} not found")
        return 1

    print("=" * 80)
    print("SSMD/SSML Comparison Script")
    print("=" * 80)

    # Read input files
    print(f"\n1. Reading {ssmd_file.name}...")
    ssmd_text = ssmd_file.read_text(encoding="utf-8")

    print(f"2. Reading {ssml_file.name}...")
    ssml_expected = ssml_file.read_text(encoding="utf-8")

    # Test 1: SSMD → SSML
    print(f"\n3. Converting SSMD → SSML and writing to {ssml_out_file.name}...")
    ssml_generated = ssmd.to_ssml(ssmd_text)
    with open(ssml_out_file, "w", encoding="utf-8") as f:
        f.write(ssml_generated)
    
    print(f"\n4. Reading {ssml_out_file.name}...")
    ssml_gen_text = ssml_out_file.read_text(encoding="utf-8")
    
    print(f"\n5. Converting SSML back to SSMD and writing to {ssmd_returned_file.name}...")
    ssmd_returned = ssmd.from_ssml(ssml_gen_text)
    with open(ssmd_returned_file, "w", encoding="utf-8") as f:
        f.write(ssmd_returned)

    # Test 2: SSML → SSMD
    print(f"\n6. Converting SSML → SSMD and writing to {ssmd_out_file.name}...")
    ssmd_generated = ssmd.from_ssml(ssml_expected)
    with open(ssmd_out_file, "w", encoding="utf-8") as f:
        f.write(ssmd_generated)

    print(f"\n7. Reading {ssmd_out_file.name}...")
    ssmd_gen_text = ssmd_out_file.read_text(encoding="utf-8")
    
    print(f"\n8. Converting SSMD back to SSML and writing to {ssml_returned_file.name}...")
        
    ssml_returned = ssmd.from_ssml(ssmd_gen_text)
    with open(ssml_returned_file, "w", encoding="utf-8") as f:
        f.write(ssml_returned)

    return 0


if __name__ == "__main__":
    sys.exit(main())
