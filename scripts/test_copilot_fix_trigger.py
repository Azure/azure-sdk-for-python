#!/usr/bin/env python3
"""
Test script to verify the copilot_fix_trigger.py script works correctly.

This script tests the basic functionality of the Copilot fix trigger script
without requiring actual GitHub issues.
"""

import json
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

try:
    from copilot_fix_trigger import (
        get_fix_instructions,
        generate_copilot_prompt,
    )
except ImportError as e:
    print(f"Error importing copilot_fix_trigger: {e}")
    sys.exit(1)


def test_get_fix_instructions():
    """Test that fix instructions are generated for all tools."""
    print("Testing get_fix_instructions...")
    
    tools = ["mypy", "pylint", "pyright"]
    for tool in tools:
        instructions = get_fix_instructions(tool)
        assert instructions, f"No instructions for {tool}"
        assert "description" in instructions, f"Missing description for {tool}"
        assert "steps" in instructions, f"Missing steps for {tool}"
        assert "reference" in instructions, f"Missing reference for {tool}"
        print(f"  ✓ {tool} instructions OK")
    
    # Test invalid tool
    invalid = get_fix_instructions("invalid")
    assert not invalid, "Should return empty dict for invalid tool"
    print("  ✓ Invalid tool handling OK")
    
    print("✓ get_fix_instructions tests passed\n")


def test_generate_copilot_prompt():
    """Test that prompts are generated correctly."""
    print("Testing generate_copilot_prompt...")
    
    tools = ["mypy", "pylint", "pyright"]
    issue_number = 12345
    
    for tool in tools:
        prompt = generate_copilot_prompt(issue_number, tool)
        assert prompt, f"No prompt generated for {tool}"
        assert str(issue_number) in prompt, f"Issue number not in prompt for {tool}"
        assert tool in prompt.lower(), f"Tool name not in prompt for {tool}"
        assert "azure-ai-ml" in prompt, f"Package name not in prompt for {tool}"
        assert "Steps to follow:" in prompt, f"Missing steps section for {tool}"
        assert "Reference Documentation:" in prompt, f"Missing reference section for {tool}"
        print(f"  ✓ {tool} prompt OK")
    
    # Test invalid tool
    invalid_prompt = generate_copilot_prompt(issue_number, "invalid")
    assert "Error:" in invalid_prompt, "Should return error for invalid tool"
    print("  ✓ Invalid tool prompt OK")
    
    print("✓ generate_copilot_prompt tests passed\n")


def test_prompt_content():
    """Test that prompts contain expected content."""
    print("Testing prompt content...")
    
    issue_number = 44424
    
    # Test mypy prompt
    mypy_prompt = generate_copilot_prompt(issue_number, "mypy")
    assert "tox -e mypy" in mypy_prompt, "Missing tox command for mypy"
    assert "static_type_checking_cheat_sheet.md" in mypy_prompt, "Missing mypy reference"
    print("  ✓ mypy prompt content OK")
    
    # Test pylint prompt
    pylint_prompt = generate_copilot_prompt(issue_number, "pylint")
    assert "tox -e pylint" in pylint_prompt, "Missing tox command for pylint"
    assert "pylint_checking.md" in pylint_prompt, "Missing pylint reference"
    print("  ✓ pylint prompt content OK")
    
    # Test pyright prompt
    pyright_prompt = generate_copilot_prompt(issue_number, "pyright")
    assert "pyright" in pyright_prompt.lower(), "Missing pyright command"
    assert "static_type_checking_cheat_sheet.md" in pyright_prompt, "Missing pyright reference"
    print("  ✓ pyright prompt content OK")
    
    # Check common elements
    for tool in ["mypy", "pylint", "pyright"]:
        prompt = generate_copilot_prompt(issue_number, tool)
        assert "minimal changes" in prompt.lower(), f"Missing minimal changes note for {tool}"
        assert "tests pass" in prompt.lower(), f"Missing test requirement for {tool}"
        assert f"PR linked to issue #{issue_number}" in prompt, f"Missing PR link requirement for {tool}"
    
    print("✓ prompt content tests passed\n")


def main():
    """Run all tests."""
    print("=" * 70)
    print("Testing copilot_fix_trigger.py")
    print("=" * 70 + "\n")
    
    try:
        test_get_fix_instructions()
        test_generate_copilot_prompt()
        test_prompt_content()
        
        print("=" * 70)
        print("✓ All tests passed!")
        print("=" * 70)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
