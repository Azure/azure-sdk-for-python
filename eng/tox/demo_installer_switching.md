# Tox Installer Switching Demo

This document demonstrates how to use the new environment variable-based installer switching in the tox.ini configuration.

## Configuration Overview

The `eng/tox/tox.ini` file now supports switching between standard `pip` and `uv` using environment variables:

- `TOX_PIP_IMPL`: Controls which pip implementation to use (`pip` or `uv`)
- `TOX_CACHE_OPTION`: Controls caching behavior (optional)

## Usage Examples

### Using standard pip (default behavior)
```bash
# These all use standard pip (the default)
tox -e pylint
TOX_PIP_IMPL=pip tox -e pylint
```

### Using uv for faster installation
```bash
# Use uv for faster installation
TOX_PIP_IMPL=uv tox -e pylint
```

### Testing the configuration
```bash
# Test with standard pip (default)
echo "Testing with standard pip:"
TOX_PIP_IMPL=pip tox --version

# Test with uv  
echo "Testing with uv:"
TOX_PIP_IMPL=uv tox --version
```

## PowerShell Examples (Windows)

```powershell
# Using standard pip (default)
tox -e pylint

# Using uv for faster installation
$env:TOX_PIP_IMPL="uv"; tox -e pylint

# Using standard pip without cache
$env:TOX_PIP_IMPL="pip"; $env:TOX_CACHE_OPTION=""; tox -e pylint
```

## Implementation Details

The configuration uses these tox.ini variables:
- `{[tox]pip_impl}` - Resolves to either "pip" or "uv"
- `{[tox]pip_command}` - Resolves to "pip pip" (which becomes just "pip") or "uv pip"
- `{[tox]cache_option}` - Handles cache directory options

This approach maintains backward compatibility while providing flexibility for different environments and use cases.
