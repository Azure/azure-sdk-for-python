---
name: sdk-py-setup
description: Guide SDK users through setting up their Python environment for Azure AI Content Understanding. Use this skill when users need help installing the SDK, configuring Azure resources, deploying required models, setting environment variables, or running samples.
---

# SDK User Environment Setup for Azure AI Content Understanding

Set up your Python environment to use the Azure AI Content Understanding SDK and run samples.

> **Note:** This skill is for SDK users who want to run samples and use the SDK. For SDK development, see the `sdkinternal-py-setup` skill.

## Prerequisites

Before starting, ensure you have:

- **Python 3.9 or later** installed
- An **Azure subscription** ([create one for free](https://azure.microsoft.com/free/))
- A **Microsoft Foundry resource** in a [supported region](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support)

## Package Directory

```
sdk/contentunderstanding/azure-ai-contentunderstanding
```

## Workflow

### Step 1: Navigate to Package Directory

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding
```

### Step 2: Create and Activate Virtual Environment

**Check and create virtual environment:**

```bash
if [ -d ".venv" ]; then
    echo "Virtual environment already exists at .venv"
else
    echo "Creating virtual environment..."
    python -m venv .venv
    echo "Virtual environment created at .venv"
fi
```

**Activate virtual environment:**

| Platform | Command |
|----------|---------|
| Linux/macOS | `source .venv/bin/activate` |
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows Command Prompt | `.venv\Scripts\activate.bat` |

**Verify activation:**
```bash
which python  # Linux/macOS
# where python  # Windows
# Should show path inside .venv
```

### Step 3: Install SDK and Dependencies

Install the SDK and all required dependencies using `dev_requirements.txt`:

```bash
pip install azure-ai-contentunderstanding
pip install -r dev_requirements.txt
```

This installs all dependencies needed to run samples:
- `aiohttp` - Required for async operations
- `python-dotenv` - For loading `.env` files
- `azure-identity` - For `DefaultAzureCredential` authentication

### Step 4: Configure Environment Variables

#### 4.1 Copy env.sample to .env (with safety check)

**Important:** This step copies the template without overwriting any existing `.env` file.

```bash
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists - NOT overwriting"
    echo "If you want to start fresh, manually delete .env first: rm .env"
else
    cp env.sample .env
    echo "✅ Created .env from env.sample"
    echo "Please edit .env and configure the required variables (see Step 4.2)"
fi
```

**For Windows PowerShell:**
```powershell
if (Test-Path ".env") {
    Write-Host "⚠️  .env file already exists - NOT overwriting"
    Write-Host "If you want to start fresh, manually delete .env first: Remove-Item .env"
} else {
    Copy-Item env.sample .env
    Write-Host "✅ Created .env from env.sample"
    Write-Host "Please edit .env and configure the required variables (see Step 4.2)"
}
```

#### 4.2 Configure Required Variables

Open `.env` in your editor and set the following **required** variables:

| Variable | Description | How to Get It |
|----------|-------------|---------------|
| `CONTENTUNDERSTANDING_ENDPOINT` | Your Microsoft Foundry endpoint URL | Azure Portal → Your Foundry resource → Keys and Endpoint |
| `CONTENTUNDERSTANDING_KEY` | API key (optional if using DefaultAzureCredential) | Azure Portal → Your Foundry resource → Keys and Endpoint → Key1 or Key2 |

**For running `sample_update_defaults.py` (one-time model configuration):**

| Variable | Description | How to Get It |
|----------|-------------|---------------|
| `GPT_4_1_DEPLOYMENT` | Your GPT-4.1 deployment name | Microsoft Foundry → Deployments → Your GPT-4.1 deployment name |
| `GPT_4_1_MINI_DEPLOYMENT` | Your GPT-4.1-mini deployment name | Microsoft Foundry → Deployments → Your GPT-4.1-mini deployment name |
| `TEXT_EMBEDDING_3_LARGE_DEPLOYMENT` | Your text-embedding-3-large deployment name | Microsoft Foundry → Deployments → Your embedding deployment name |

#### 4.3 Validate Your Configuration

**Ask yourself these questions before proceeding:**

1. ✅ **Is `CONTENTUNDERSTANDING_ENDPOINT` set?**
   - Should look like: `https://<your-resource-name>.services.ai.azure.com/`
   - Check: Does NOT include `api-version` or other query parameters

2. ✅ **Authentication configured?**
   - **Option A (API Key):** Is `CONTENTUNDERSTANDING_KEY` set with a valid key?
   - **Option B (DefaultAzureCredential):** Have you run `az login` to authenticate?

3. ✅ **For prebuilt analyzers - Are model deployments configured?**
   - Have you deployed the required models in Microsoft Foundry?
   - Are `GPT_4_1_DEPLOYMENT`, `GPT_4_1_MINI_DEPLOYMENT`, `TEXT_EMBEDDING_3_LARGE_DEPLOYMENT` set to match your deployment names?

**Example `.env` configuration:**
```bash
# Required for all samples
CONTENTUNDERSTANDING_ENDPOINT=https://my-foundry-resource.services.ai.azure.com/

# Optional: API key (if not set, DefaultAzureCredential is used)
CONTENTUNDERSTANDING_KEY=abc123...

# Required for sample_update_defaults.py (model configuration)
GPT_4_1_DEPLOYMENT=gpt-4.1
GPT_4_1_MINI_DEPLOYMENT=gpt-4.1-mini
TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=text-embedding-3-large
```

### Step 5: Azure Resource Setup (if not done)

If you haven't set up your Microsoft Foundry resource yet:

#### 5.1 Create Microsoft Foundry Resource

1. Go to [Azure Portal](https://portal.azure.com/)
2. Create a **Microsoft Foundry resource** in a [supported region](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support)
3. Navigate to **Resource Management** > **Keys and Endpoint**
4. Copy the **Endpoint** URL and optionally a **Key**

#### 5.2 Grant Cognitive Services User Role

This role is required even if you own the resource:

1. In your Foundry resource, go to **Access Control (IAM)**
2. Click **Add** > **Add role assignment**
3. Select **Cognitive Services User** role
4. Assign it to yourself

#### 5.3 Deploy Required Models

| Analyzer Type | Required Models |
|--------------|-----------------|
| `prebuilt-documentSearch`, `prebuilt-imageSearch`, `prebuilt-audioSearch`, `prebuilt-videoSearch` | gpt-4.1-mini, text-embedding-3-large |
| Other prebuilt analyzers (invoice, receipt, etc.) | gpt-4.1, text-embedding-3-large |

**To deploy a model:**
1. In Microsoft Foundry → **Deployments** → **Deploy model** → **Deploy base model**
2. Search and deploy: `gpt-4.1`, `gpt-4.1-mini`, `text-embedding-3-large`
3. Note deployment names (recommendation: use model name as deployment name)

### Step 6: Configure Model Defaults (One-Time Setup)

Run the configuration script to map deployed models to prebuilt analyzers:

```bash
cd samples
python sample_update_defaults.py
```

This is a **one-time setup per Microsoft Foundry resource**.

### Step 7: Run Samples

#### Sync Samples

```bash
# From the package directory with venv activated
cd samples

# Run sync samples
python sample_analyze_url.py
python sample_analyze_binary.py
```

#### Async Samples

```bash
cd samples/async_samples

# Run async samples
python sample_analyze_url_async.py
python sample_analyze_binary_async.py
```

## Automated Setup Script (Linux/macOS)

Run the interactive setup script that handles all steps automatically:

```bash
# From the package directory
cd sdk/contentunderstanding/azure-ai-contentunderstanding
.github/skills/sdk-py-setup/scripts/setup_user_env.sh
```

The script will:
1. Create and activate a virtual environment
2. Install the SDK and dependencies
3. Copy `env.sample` to `.env` (without overwriting existing)
4. Interactively prompt you to configure required environment variables

### Manual Quick Setup

If you prefer to run steps manually:

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding

# Create and activate venv
[ ! -d ".venv" ] && python -m venv .venv
source .venv/bin/activate

# Install SDK and dependencies
pip install azure-ai-contentunderstanding
pip install -r dev_requirements.txt

# Copy env.sample if .env doesn't exist
if [ ! -f ".env" ]; then
    cp env.sample .env
    echo "✅ Created .env - Please edit and configure required variables"
else
    echo "⚠️  .env already exists - skipping copy"
fi
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| `python: command not found` | Ensure Python 3.9+ is installed. Try `python3` instead of `python`. |
| `ModuleNotFoundError` after running sample | Ensure venv is activated: `source .venv/bin/activate`. Reinstall: `pip install -r dev_requirements.txt` |
| `Access denied due to invalid subscription key` | Verify `CONTENTUNDERSTANDING_ENDPOINT` URL is correct. Check API key or run `az login`. |
| `Model deployment not found` | Deploy required models in Microsoft Foundry. Run `sample_update_defaults.py`. |
| `Cognitive Services User role not assigned` | Add the role in Azure Portal → Your resource → Access Control (IAM). |

## Additional Resources

- [SDK README](../../../README.md) - Full documentation
- [Samples README](../../../samples/README.md) - Sample descriptions
- [Product Documentation](https://learn.microsoft.com/azure/ai-services/content-understanding/)
- [Prebuilt Analyzers](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers)
