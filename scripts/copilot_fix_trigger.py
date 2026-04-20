#!/usr/bin/env python3
"""
Script to help trigger Copilot fixes for azure-ai-ml linting/type checking issues.

This script can be used to generate instructions for Copilot to fix specific
issues related to mypy, pylint, or pyright in the azure-ai-ml package.

Usage:
    python scripts/copilot_fix_trigger.py --issue-number 44424 --tool mypy
    python scripts/copilot_fix_trigger.py --issue-number 44424 --tool pylint
    python scripts/copilot_fix_trigger.py --issue-number 44424 --tool pyright
"""

import argparse
import json
import os
import sys
from pathlib import Path


def get_fix_instructions(tool: str, package: str = "azure-ai-ml") -> dict:
    """Get fix instructions for a specific tool and package."""
    
    instructions = {
        "mypy": {
            "description": "Fix mypy type checking errors",
            "steps": [
                f"Navigate to sdk/ml/{package}",
                "Run: tox -e mypy -- sdk/ml/azure-ai-ml",
                "Review the mypy errors",
                "Fix type annotations and type errors",
                "Re-run mypy to verify fixes",
                "Run tests to ensure no regressions",
            ],
            "reference": "https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md",
        },
        "pylint": {
            "description": "Fix pylint warnings and errors",
            "steps": [
                f"Navigate to sdk/ml/{package}",
                "Run: tox -e pylint --c eng/tox/tox.ini --root .",
                "Review the pylint warnings",
                "Fix code style and convention issues",
                "Re-run pylint to verify fixes",
                "Run tests to ensure no regressions",
            ],
            "reference": "https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md",
        },
        "pyright": {
            "description": "Fix pyright type checking errors",
            "steps": [
                f"Navigate to sdk/ml/{package}",
                "Run: pyright",
                "Review the pyright errors",
                "Fix type annotations and type errors",
                "Re-run pyright to verify fixes",
                "Run tests to ensure no regressions",
            ],
            "reference": "https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md",
        },
    }
    
    return instructions.get(tool.lower(), {})


def generate_copilot_prompt(issue_number: int, tool: str, package: str = "azure-ai-ml") -> str:
    """Generate a prompt for Copilot to fix the issue."""
    
    instructions = get_fix_instructions(tool, package)
    
    if not instructions:
        return f"Error: Unknown tool '{tool}'. Supported tools: mypy, pylint, pyright"
    
    prompt = f"""Fix {tool} issues in {package} package (Issue #{issue_number})

**Task:** {instructions['description']} in the {package} package.

**Steps to follow:**
"""
    
    for i, step in enumerate(instructions['steps'], 1):
        prompt += f"{i}. {step}\n"
    
    prompt += f"""
**Reference Documentation:**
{instructions['reference']}

**Important Notes:**
- Make minimal changes necessary to fix the issues
- Ensure all tests pass after making changes
- Follow the Azure SDK for Python design guidelines
- Do not remove or modify working code unnecessarily
- Fix only the {tool} issues, do not refactor unrelated code

**Expected Deliverables:**
1. Fixed {tool} issues in {package}
2. All tests passing
3. No regressions introduced
4. PR linked to issue #{issue_number}
"""
    
    return prompt


def save_copilot_task(issue_number: int, tool: str, package: str = "azure-ai-ml") -> Path:
    """Save a Copilot task file for tracking."""
    
    tasks_dir = Path(".github/copilot-tasks")
    tasks_dir.mkdir(exist_ok=True)
    
    task_file = tasks_dir / f"issue-{issue_number}.json"
    
    task_data = {
        "issue_number": issue_number,
        "package": package,
        "tool": tool,
        "status": "pending",
        "prompt": generate_copilot_prompt(issue_number, tool, package),
    }
    
    with open(task_file, "w") as f:
        json.dump(task_data, f, indent=2)
    
    return task_file


def main():
    parser = argparse.ArgumentParser(
        description="Generate Copilot fix instructions for azure-ai-ml issues"
    )
    parser.add_argument(
        "--issue-number",
        type=int,
        required=True,
        help="GitHub issue number",
    )
    parser.add_argument(
        "--tool",
        type=str,
        required=True,
        choices=["mypy", "pylint", "pyright"],
        help="Tool to fix (mypy, pylint, or pyright)",
    )
    parser.add_argument(
        "--package",
        type=str,
        default="azure-ai-ml",
        help="Package name (default: azure-ai-ml)",
    )
    parser.add_argument(
        "--output-format",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format (text or json)",
    )
    parser.add_argument(
        "--save-task",
        action="store_true",
        help="Save task file for tracking",
    )
    
    args = parser.parse_args()
    
    # Generate the prompt
    prompt = generate_copilot_prompt(args.issue_number, args.tool, args.package)
    
    if args.output_format == "json":
        output = {
            "issue_number": args.issue_number,
            "tool": args.tool,
            "package": args.package,
            "prompt": prompt,
        }
        print(json.dumps(output, indent=2))
    else:
        print(prompt)
    
    # Save task file if requested
    if args.save_task:
        task_file = save_copilot_task(args.issue_number, args.tool, args.package)
        print(f"\nTask file saved: {task_file}", file=sys.stderr)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
