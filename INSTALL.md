# Azure SDK for Python - Root Installation

## Overview

The root of this repository contains a `pyproject.toml` and an `install_packages.py` script that can discover and install all Azure SDK packages in the repository.

## Installation Methods

### Method 1: Using the install script directly (Recommended)

To install all Azure SDK packages:

```bash
python install_packages.py install
```

To install packages in development/editable mode:

```bash
python install_packages.py develop
```

To see available packages without installing:

```bash
python install_packages.py --version
```

### Method 2: Using pip with the root package

After installing this root package, you can use the CLI tool:

```bash
# Install the root package first
pip install .

# Then use the CLI tool
install-azure-sdk-packages install
```

## How It Works

The installation script:

1. **Discovers packages** by searching for:
   - `azure*/setup.py` and `azure*/pyproject.toml` at the root level
   - `sdk/*/azure*/setup.py` and `sdk/*/azure*/pyproject.toml` in SDK directories

2. **Determines installation method** for each package:
   - Packages with `pyproject.toml` containing `[project]` section → Uses `pip install`
   - Packages with `setup.py` → Uses traditional setuptools
   - Packages with both → Prefers `setup.py` for backward compatibility

3. **Installs packages** in the correct order:
   - Namespace packages (nspkg) first
   - `azure-common` (if present)
   - All other content packages

## Package Types Supported

- **Modern pyproject.toml packages** (PEP 621 compliant)
- **Traditional setup.py packages**
- **Mixed packages** (both files present)

## Examples

### Install a subset of packages

The script installs all discovered packages. To install specific packages, use pip directly:

```bash
pip install ./sdk/core/azure-core
pip install ./sdk/ai/azure-ai-projects
```

### Verify package discovery

To see which packages will be discovered without installing:

```bash
python install_packages.py --version
```

This will list all packages found in the repository.

## Migration from setup.py

Previously, this repository had a `setup.py` at the root. This has been replaced with:
- `pyproject.toml` - Modern Python package configuration (PEP 621)
- `install_packages.py` - Installation orchestration script

The functionality remains the same, but now uses standard Python packaging tools.
