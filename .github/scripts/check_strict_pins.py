#!/usr/bin/env python3
"""
Script to detect strict version pins (==) in Python package dependencies.

This script checks for new strict version pins introduced in setup.py and pyproject.toml
files within the sdk directory, focusing on main runtime dependencies (install_requires
for setup.py, [project] dependencies for pyproject.toml).

It ignores:
- dev/test/extras dependencies
- comments
- Changes outside of main dependency sections
"""

import os
import re
import subprocess
import sys
from typing import Dict, List, Set, Tuple
import json
import urllib.request
import urllib.parse


def run_git_command(cmd: List[str]) -> str:
    """Run a git command and return its output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e}")
        print(f"stderr: {e.stderr}")
        return ""


def get_changed_files(base_ref: str, head_ref: str) -> List[str]:
    """Get list of changed setup.py and pyproject.toml files in sdk directory."""
    diff_output = run_git_command([
        "git", "diff", "--name-only", "--diff-filter=AM",
        base_ref, head_ref
    ])
    
    files = []
    for line in diff_output.strip().split('\n'):
        if line:
            if (line.startswith('sdk/') and 
                (line.endswith('/setup.py') or line.endswith('/pyproject.toml'))):
                files.append(line)
    
    return files


def extract_strict_pins_from_setup_py_diff(diff_content: str) -> List[str]:
    """
    Extract strict version pins from a setup.py diff.
    Only considers additions in install_requires section.
    """
    strict_pins = []
    in_install_requires = False
    bracket_depth = 0
    
    for line in diff_content.split('\n'):
        # Skip the +++ file marker
        if line.startswith('+++') or line.startswith('---'):
            continue
        
        # Process all lines to track context, but only extract from added lines
        actual_line = line[1:].strip() if (line.startswith('+') or line.startswith('-') or line.startswith(' ')) else line.strip()
        
        # Detect start of install_requires in any line
        if 'install_requires' in actual_line and '=' in actual_line:
            in_install_requires = True
            bracket_depth = 0
            # Check if the array starts on the same line
            if '[' in actual_line:
                bracket_depth = actual_line.count('[') - actual_line.count(']')
        
        # Detect end of install_requires or start of other sections
        if in_install_requires:
            if 'extras_require' in actual_line or 'tests_require' in actual_line:
                in_install_requires = False
                continue
            
            # Track brackets in all lines
            bracket_depth += actual_line.count('[') - actual_line.count(']')
            
            # If we close all brackets, we're done with install_requires
            if bracket_depth <= 0 and (']' in actual_line or '),' in actual_line):
                # Check current line before exiting if it's an added line
                if line.startswith('+') and '==' in actual_line and not actual_line.strip().startswith('#'):
                    match = re.search(r'["\']([^"\']+==[\d\.]+[^"\']*)["\']', actual_line)
                    if match:
                        strict_pins.append(match.group(1))
                in_install_requires = False
                continue
        
        # Look for strict pins in added lines within install_requires
        if in_install_requires and line.startswith('+'):
            if '==' in actual_line and not actual_line.strip().startswith('#'):
                # Match package==version pattern
                match = re.search(r'["\']([^"\']+==[\d\.]+[^"\']*)["\']', actual_line)
                if match:
                    strict_pins.append(match.group(1))
    
    return strict_pins


def extract_strict_pins_from_pyproject_diff(diff_content: str) -> List[str]:
    """
    Extract strict version pins from a pyproject.toml diff.
    Only considers additions in [project] dependencies section.
    """
    strict_pins = []
    in_project_dependencies = False
    in_other_section = False
    
    for line in diff_content.split('\n'):
        # Skip the +++ and --- file markers
        if line.startswith('+++') or line.startswith('---'):
            continue
        
        # Process all lines to track context
        actual_line = line[1:].strip() if (line.startswith('+') or line.startswith('-') or line.startswith(' ')) else line.strip()
        
        # Detect [project] section markers in any line (context or changes)
        if actual_line.startswith('['):
            if actual_line.startswith('[project]'):
                in_other_section = False
            elif actual_line.startswith('['):
                in_other_section = True
                in_project_dependencies = False
        
        # Detect start of dependencies in [project] section
        if not in_other_section and 'dependencies' in actual_line and '=' in actual_line:
            if not ('optional-dependencies' in actual_line or 
                    'dev-dependencies' in actual_line):
                in_project_dependencies = True
                continue
        
        # Detect end of dependencies array
        if in_project_dependencies and ']' in actual_line and '==' not in actual_line:
            in_project_dependencies = False
            continue
        
        # Look for strict pins in added lines within [project] dependencies
        if in_project_dependencies and line.startswith('+'):
            if '==' in actual_line and not actual_line.strip().startswith('#'):
                # Match package==version pattern  
                match = re.search(r'["\']([^"\']+==[\d\.]+[^"\']*)["\']', actual_line)
                if match:
                    strict_pins.append(match.group(1))
    
    return strict_pins


def check_file_for_strict_pins(filepath: str, base_ref: str, head_ref: str) -> List[str]:
    """Check a specific file for new strict version pins."""
    # Get the diff for this file
    diff_output = run_git_command([
        "git", "diff", base_ref, head_ref, "--", filepath
    ])
    
    if not diff_output:
        return []
    
    if filepath.endswith('setup.py'):
        return extract_strict_pins_from_setup_py_diff(diff_output)
    elif filepath.endswith('pyproject.toml'):
        return extract_strict_pins_from_pyproject_diff(diff_output)
    
    return []


def check_architect_approval(pr_number: str, repo: str, github_token: str) -> bool:
    """
    Check if any of the architects have approved the PR.
    Architects: kashifkhan, annatisch, johanste
    """
    architects = {'kashifkhan', 'annatisch', 'johanste'}
    
    # GitHub API to get PR reviews
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            reviews = json.loads(response.read())
        
        for review in reviews:
            if review['state'] == 'APPROVED':
                reviewer = review['user']['login']
                if reviewer in architects:
                    print(f"✅ Architect {reviewer} has approved this PR")
                    return True
        
        print("❌ No architect approval found")
        return False
        
    except Exception as e:
        print(f"Error checking PR reviews: {e}")
        # In case of error, we should fail open to not block legitimate PRs
        # if the API is down
        return False


def set_output(name: str, value: str):
    """Set GitHub Actions output."""
    github_output = os.getenv('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            # Escape newlines and special characters
            escaped_value = value.replace('%', '%25').replace('\n', '%0A').replace('\r', '%0D')
            f.write(f"{name}={escaped_value}\n")
    else:
        print(f"::set-output name={name}::{value}")


def main():
    base_ref = os.getenv('BASE_REF', 'origin/main')
    head_ref = os.getenv('HEAD_REF', 'HEAD')
    pr_number = os.getenv('PR_NUMBER')
    repo = os.getenv('REPO')
    github_token = os.getenv('GITHUB_TOKEN')
    
    print(f"Checking for strict version pins...")
    print(f"Base: {base_ref}, Head: {head_ref}")
    
    # Get changed files
    changed_files = get_changed_files(base_ref, head_ref)
    
    if not changed_files:
        print("No relevant files changed")
        set_output('strict_pins_found', 'false')
        set_output('architect_approved', 'false')
        set_output('strict_pins_details', '')
        return 0
    
    print(f"Checking {len(changed_files)} file(s):")
    for f in changed_files:
        print(f"  - {f}")
    
    # Check each file for strict pins
    all_strict_pins = {}
    for filepath in changed_files:
        strict_pins = check_file_for_strict_pins(filepath, base_ref, head_ref)
        if strict_pins:
            all_strict_pins[filepath] = strict_pins
    
    if not all_strict_pins:
        print("✅ No new strict version pins found")
        set_output('strict_pins_found', 'false')
        set_output('architect_approved', 'false')
        set_output('strict_pins_details', '')
        return 0
    
    # Format the findings
    details = []
    for filepath, pins in all_strict_pins.items():
        details.append(f"{filepath}:")
        for pin in pins:
            details.append(f"  - {pin}")
    
    details_str = '\n'.join(details)
    print(f"\n⚠️  Strict version pins found:\n{details_str}")
    
    # Check for architect approval
    architect_approved = False
    if pr_number and repo and github_token:
        architect_approved = check_architect_approval(pr_number, repo, github_token)
    
    set_output('strict_pins_found', 'true')
    set_output('architect_approved', 'true' if architect_approved else 'false')
    set_output('strict_pins_details', details_str)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
