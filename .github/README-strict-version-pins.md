# Strict Version Pin Check Workflow

## Overview

This GitHub Actions workflow enforces a policy that requires architect approval for any pull requests that introduce strict version pins (`==`) in main runtime dependencies of Python packages within the `sdk/` directory.

## Purpose

Strict version pins can cause dependency conflicts and limit flexibility in package management. This workflow ensures that any such pins in main runtime dependencies are reviewed and approved by designated architects before merging.

## How It Works

### Trigger
The workflow runs on pull requests that modify:
- `sdk/**/setup.py`
- `sdk/**/pyproject.toml`

### Detection Logic

The workflow analyzes the diff to detect:
- **New strict version pins**: Dependencies newly added with `==` operator
- **Modified pins**: Dependencies changed from flexible constraints (e.g., `>=`, `~=`) to strict `==` pins

The detection is **scope-aware** and only considers:
- `install_requires` in `setup.py`
- `dependencies` under `[project]` in `pyproject.toml`

The following are **ignored**:
- Dev dependencies (`extras_require`, `[project.optional-dependencies]`)
- Test dependencies (`tests_require`)
- Comments
- Build dependencies

### Approval Requirements

If strict version pins are detected, the workflow:
1. Posts a comment on the PR listing the detected pins
2. Checks if any of the following architects have approved the PR:
   - `@kashifkhan`
   - `@annatisch`
   - `@johanste`
3. **Blocks merging** if no architect approval is found (workflow fails with exit code 1)
4. **Allows merging** if an architect has approved

### CODEOWNERS Integration

The `.github/CODEOWNERS` file has been updated to require reviews from the architects for:
- `/sdk/**/setup.py`
- `/sdk/**/pyproject.toml`

This provides a secondary enforcement mechanism through branch protection rules.

## Examples

### ✅ Allowed (No Strict Pins)
```python
# setup.py
install_requires=[
    "azure-core>=1.30.0",
    "requests>=2.21.0",
]
```

### ⚠️ Requires Architect Approval
```python
# setup.py
install_requires=[
    "azure-core==1.30.0",  # Strict pin detected!
    "requests>=2.21.0",
]
```

### ✅ Allowed (Strict Pin in Dev Dependencies)
```python
# setup.py
install_requires=[
    "azure-core>=1.30.0",
],
extras_require={
    "dev": ["pytest==7.0.0"]  # OK - this is a dev dependency
}
```

## Testing

The detection logic has been validated with comprehensive test cases covering:
- Adding new strict pins
- Changing from flexible to strict constraints
- Ignoring dev/test dependencies
- Ignoring optional dependencies in pyproject.toml

Run tests locally:
```bash
python /tmp/test_strict_pins.py
```

## Files Modified

1. **`.github/workflows/check-strict-version-pins.yml`**
   - Main workflow definition
   - Triggers on PR events
   - Runs detection and enforcement logic

2. **`.github/scripts/check_strict_pins.py`**
   - Python script that analyzes git diffs
   - Detects strict version pins in appropriate sections
   - Checks for architect approvals via GitHub API

3. **`.github/CODEOWNERS`**
   - Added architect requirements for setup.py and pyproject.toml

## Branch Protection

To fully enforce this policy, ensure branch protection rules are configured to:
- Require status checks to pass before merging
- Require the "check-strict-pins" workflow to succeed
- Require review from code owners

## Troubleshooting

### Workflow Not Running
- Verify the PR modifies files matching `sdk/**/setup.py` or `sdk/**/pyproject.toml`
- Check workflow runs in the Actions tab

### False Positives
If the workflow incorrectly flags a dependency:
- Verify the dependency is in the main runtime dependencies section
- Check if comments are interfering with detection
- File an issue with the specific case

### Override Process
If a strict pin is necessary:
1. Document the justification in the PR description
2. Request review from one of the architects:
   - @kashifkhan
   - @annatisch
   - @johanste
3. Architect provides approval review
4. Workflow will pass and allow merge

## Maintenance

### Adding/Removing Architects
To modify the list of architects:
1. Update the `architects` set in `.github/scripts/check_strict_pins.py`
2. Update the CODEOWNERS entries in `.github/CODEOWNERS`
3. Update documentation in this README

### Extending Detection
To add support for additional dependency formats:
1. Add extraction function in `check_strict_pins.py`
2. Update `check_file_for_strict_pins()` to handle new file types
3. Add corresponding test cases
4. Update workflow triggers if needed
