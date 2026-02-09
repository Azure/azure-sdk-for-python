---
name: sdkinternal-py-setup
description: Set up Python virtual environment for azure-ai-contentunderstanding package development. Use this skill when setting up the development environment, creating venv, installing dependencies, or configuring environment variables.
---

# Python Virtual Environment Setup for azure-ai-contentunderstanding

Set up a complete Python development environment for the azure-ai-contentunderstanding package, including virtual environment creation, dependency installation, and environment configuration.

## Package Directory

```
sdk/contentunderstanding/azure-ai-contentunderstanding
```

## Workflow

### 1. Navigate to Package Directory

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding
```

### 2. Check and Create Virtual Environment

Check if the virtual environment already exists:

```bash
if [ -d ".venv" ]; then
    echo "Virtual environment already exists at .venv"
else
    echo "Creating virtual environment..."
    python -m venv .venv
    echo "Virtual environment created at .venv"
fi
```

### 3. Activate Virtual Environment

**On Linux/macOS:**
```bash
source .venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

Verify activation by checking Python location:
```bash
which python  # Linux/macOS
# where python  # Windows
```

### 4. Install Dependencies

Install the SDK and all development dependencies:

```bash
pip install -e .
pip install -r dev_requirements.txt
```

This installs:
- `aiohttp` - Required for async operations
- `python-dotenv` - For loading `.env` files
- `azure-identity` - For `DefaultAzureCredential` authentication
- `pytest-xdist` - For parallel test execution

### 5. Configure Environment Variables

Check if `.env` file exists in the package root directory:

```bash
if [ -f ".env" ]; then
    echo ".env file already exists"
else
    echo "Copying env.sample to .env..."
    cp env.sample .env
    echo "Created .env - Please configure the required variables"
fi
```

### 6. Required Environment Variables

After copying, edit `.env` and configure these **required** variables:

| Variable | Description | Required For |
|----------|-------------|--------------|
| `CONTENTUNDERSTANDING_ENDPOINT` | Microsoft Foundry resource endpoint URL (e.g., `https://<your-resource>.services.ai.azure.com/`) | All samples |
| `CONTENTUNDERSTANDING_KEY` | API key (optional if using DefaultAzureCredential) | API key authentication |
| `GPT_4_1_DEPLOYMENT` | GPT-4.1 deployment name in Microsoft Foundry | sample_update_defaults.py |
| `GPT_4_1_MINI_DEPLOYMENT` | GPT-4.1-mini deployment name | sample_update_defaults.py |
| `TEXT_EMBEDDING_3_LARGE_DEPLOYMENT` | text-embedding-3-large deployment name | sample_update_defaults.py |

**Example `.env` configuration:**
```bash
CONTENTUNDERSTANDING_ENDPOINT=https://<your-resource-name>.services.ai.azure.com/
CONTENTUNDERSTANDING_KEY=<your-api-key>  # Optional if using DefaultAzureCredential
GPT_4_1_DEPLOYMENT=gpt-4.1
GPT_4_1_MINI_DEPLOYMENT=gpt-4.1-mini
TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=text-embedding-3-large
```

### 7. Verify Setup

Test the environment by running a sample:

```bash
cd samples
python sample_update_defaults.py
```

## Complete Setup Script (Linux/macOS)

Run the automated setup script:

```bash
# From the package directory
.github/skills/sdkinternal-py-setup/scripts/setup_venv.sh
```

Or run all steps manually:

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding

# Create venv if not exists
[ ! -d ".venv" ] && python -m venv .venv

# Activate
source .venv/bin/activate

# Install dependencies
pip install -e .
pip install -r dev_requirements.txt

# Copy env.sample if .env doesn't exist
[ ! -f ".env" ] && cp env.sample .env && echo "Created .env - configure required variables"

echo "Setup complete! Edit .env with your configuration."
```

## Troubleshooting

**Error: "python: command not found"**
- Ensure Python 3.9+ is installed
- Try using `python3` instead of `python`

**Error: "pip: command not found" after activation**
- The venv may not have pip. Run: `python -m ensurepip --upgrade`

**Error: "ModuleNotFoundError" when running samples**
- Ensure venv is activated: `source .venv/bin/activate`
- Reinstall dependencies: `pip install -r dev_requirements.txt`

**Error: "Access denied" or authentication failures**
- Check `CONTENTUNDERSTANDING_ENDPOINT` is correct
- If using API key, verify `CONTENTUNDERSTANDING_KEY` is set
- If using DefaultAzureCredential, run `az login` first
