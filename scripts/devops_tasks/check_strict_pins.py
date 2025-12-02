#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# cspell:ignore pyproject kashifkhan annatisch johanste
"""
Detects strict dependency version pins (==) in Python package dependencies.

Checks setup.py (install_requires) and pyproject.toml ([project] dependencies)
for new strict dependency version pins. Requires architect approval to proceed.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Dict, List

from ci_tools.parsing import ParsedSetup


ARCHITECTS = {'kashifkhan', 'annatisch', 'johanste'}
STRICT_PIN_PATTERN = re.compile(r'^([a-zA-Z0-9\-_.]+)==[\d.]+')


def run_git_command(cmd: List[str]) -> str:
    """Run a git command and return its output."""
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result.stdout if result.returncode == 0 else ""


def get_changed_files(base_ref: str, head_ref: str) -> List[str]:
    """Get list of changed setup.py and pyproject.toml files in sdk directory."""
    diff_output = run_git_command([
        "git", "diff", "--name-only", "--diff-filter=AM", base_ref, head_ref
    ])
    
    return [
        line for line in diff_output.strip().split('\n')
        if line.startswith('sdk/') and (line.endswith('/setup.py') or line.endswith('/pyproject.toml'))
    ]


def check_for_new_strict_pins(filepath: str, diff_output: str) -> List[str]:
    """Check if strict pins from ParsedSetup appear in the git diff (were added)."""
    if not diff_output:
        return []
    
    # Parse current file with ParsedSetup to get all requirements
    package_dir = os.path.dirname(filepath)
    try:
        parsed = ParsedSetup.from_path(package_dir)
    except Exception as e:
        print(f"Warning: Could not parse {package_dir}: {e}")
        return []
    
    # Find strict pins that appear in added lines of the diff
    added_lines = [line for line in diff_output.split('\n') if line.startswith('+')]
    strict_pins = []
    
    for requirement in parsed.requires:
        if STRICT_PIN_PATTERN.match(requirement):
            package_name = requirement.split('==')[0]
            # Check if this package appears in added lines with ==
            if any(package_name in line and '==' in line for line in added_lines):
                strict_pins.append(requirement)
    
    return strict_pins


def check_architect_approval_via_cli(pr_number: str) -> bool:
    """Check if any architects have approved the PR using Azure CLI."""
    result = subprocess.run(
        ['az', 'repos', 'pr', 'reviewer', 'list', 
         '--id', pr_number,
         '--query', "[?vote==`10`].displayName",
         '--output', 'json'],
        capture_output=True,
        text=True,
        check=False
    )
    
    if result.returncode != 0:
        return False
    
    approvers = json.loads(result.stdout) if result.stdout else []
    return any(
        any(architect.lower() in approver.lower() for architect in ARCHITECTS)
        for approver in approvers
    )

def main() -> int:
    parser = argparse.ArgumentParser(description='Check for strict version pins in dependencies')
    parser.add_argument('--base', default='origin/main', help='Base ref for comparison')
    parser.add_argument('--head', default='HEAD', help='Head ref for comparison')
    parser.add_argument('--pr-number', help='Pull request number')
    args = parser.parse_args()
    
    # Get changed files
    changed_files = get_changed_files(args.base, args.head)
    if not changed_files:
        return 0
    
    # Check each file for new strict pins
    all_strict_pins = []
    for filepath in changed_files:
        diff_output = run_git_command([
            "git", "diff", args.base, args.head, "--", filepath
        ])
        if pins := check_for_new_strict_pins(filepath, diff_output):
            all_strict_pins += pins
    
    if not all_strict_pins:
        return 0
    
    # Print detected strict pins
    print("\n" + "=" * 80)
    print("STRICT VERSION PINS DETECTED")
    print("=" * 80)
    for pins in all_strict_pins:
        print(f"  - {pins}")
    print("\n" + "-" * 80)
    print(f"Required approvers: {', '.join(sorted(ARCHITECTS))}")
    print("-" * 80)
    
    if check_architect_approval_via_cli(args.pr_number):
        print("\nArchitect approval found")
        return 0
    
    return 1


if __name__ == '__main__':
    sys.exit(main())