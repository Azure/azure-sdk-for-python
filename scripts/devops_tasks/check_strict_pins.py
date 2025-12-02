#!/usr/bin/env python3
# cspell:ignore pyproject kashifkhan annatisch johanste
"""
Detects strict version pins (==) in Python package dependencies.

Checks setup.py (install_requires) and pyproject.toml ([project] dependencies)
for new strict version pins. Requires architect approval to proceed.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
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


def get_strict_pins(package_path: str) -> List[str]:
    """Get list of strict pins from a package using ParsedSetup."""
    try:
        parsed = ParsedSetup.from_path(package_path)
        strict_pins = []
        
        for requirement in parsed.requires:
            match = STRICT_PIN_PATTERN.match(requirement)
            if match:
                strict_pins.append(requirement)
        
        return strict_pins
    except Exception as e:
        print(f"Warning: Could not parse {package_path}: {e}")
        return []


def check_for_new_strict_pins(filepath: str, base_ref: str, head_ref: str) -> List[str]:
    """Check if new strict pins were introduced in this file."""
    package_dir = os.path.dirname(filepath)
    
    # Get current strict pins from HEAD
    current_pins = set(get_strict_pins(package_dir))
    
    # Checkout base version temporarily to check old pins
    run_git_command(["git", "checkout", base_ref, "--", filepath])
    old_pins = set(get_strict_pins(package_dir))
    
    # Restore current version
    run_git_command(["git", "checkout", head_ref, "--", filepath])
    
    # Return only newly added strict pins
    new_pins = current_pins - old_pins
    return sorted(new_pins)


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
    
    for approver in approvers:
        for architect in ARCHITECTS:
            if architect.lower() in approver.lower():
                return True
    
    return False

def print_strict_pins(all_strict_pins: Dict[str, List[str]]):
    """Print detected strict pins in a formatted way."""
    print("STRICT VERSION PINS DETECTED")
    for filepath, pins in all_strict_pins.items():
        print(f"\n{filepath}:")
        for pin in pins:
            print(f"  - {pin}")
    
    print("\n" + "-" * 80)
    print("POLICY: Strict version pins (==) require architect approval")
    print(f"Required approvers: {', '.join(sorted(ARCHITECTS))}")
    print("-" * 80)


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
    all_strict_pins = {
        filepath: pins
        for filepath in changed_files
        if (pins := check_for_new_strict_pins(filepath, args.base, args.head))
    }
    
    if not all_strict_pins:
        return 0
    
    # Found strict pins - check for approval
    print_strict_pins(all_strict_pins)
    
    if check_architect_approval_via_cli(args.pr_number):
        return 0
    
    # No approval - fail the check
    print("\nThis PR introduces strict version pins without architect approval.")
    print(f"Please request review and approval from: {', '.join(sorted(ARCHITECTS))}")
    print("=" * 80)
    return 1


if __name__ == '__main__':
    sys.exit(main())
