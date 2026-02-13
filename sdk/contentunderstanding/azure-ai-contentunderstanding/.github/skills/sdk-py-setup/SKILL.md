---
name: sdk-py-setup
description: Guide SDK users through setting up their Python environment for Azure AI Content Understanding. Use this skill when users need help installing the SDK, configuring Azure resources, deploying required models, setting environment variables, or running samples.
---

# SDK User Environment Setup for Azure AI Content Understanding

Set up your Python environment to use the Azure AI Content Understanding SDK and run samples.

> **Note:** This skill is for SDK users who want to run samples and use the SDK. For SDK development, see the `sdkinternal-py-setup` skill.

> **[COPILOT INTERACTION MODEL]:** This skill is designed to be interactive. At each step marked with **[ASK USER]**, pause execution and prompt the user for input or confirmation before proceeding. Do NOT silently skip these prompts. Use the `ask_questions` tool when available.

## Prerequisites

Before starting, ensure you have:

- **Python 3.9 or later** installed
- An **Azure subscription** ([create one for free](https://azure.microsoft.com/free/))
- A **Microsoft Foundry resource** in a [supported region](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support)

> **[ASK USER] Prerequisites Check:**
> Before proceeding, ask the user to confirm their prerequisites:
> 1. "Do you have **Python 3.9+** installed?" — If no, guide them to install Python first.
> 2. "Do you already have a **Microsoft Foundry resource** set up in Azure?" — If no, jump to **Step 5** (Azure Resource Setup) first, then return here.
> 3. "Have you already deployed the required **AI models** (GPT-4.1, GPT-4.1-mini, text-embedding-3-large) in Microsoft Foundry?" — If no, include Step 5.3 and Step 6 in the workflow.

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

> **[ASK USER] Platform:**
> Ask the user: "Which **platform** are you on?" with options:
> - Linux/macOS
> - Windows PowerShell
> - Windows Command Prompt
>
> Use their answer to show the correct activation command throughout the rest of the setup.

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

> **[ASK USER] Confirm venv:**
> After running the activation command, ask: "Does `which python` (or `where python` on Windows) show a path inside `.venv`? Please confirm the virtual environment is active before we install dependencies."
> If the user reports an error, troubleshoot before continuing.

### Step 3: Install SDK and Dependencies

> **[ASK USER] Installation mode:**
> Ask the user: "How would you like to install the SDK?"
> - **Option A: Local editable install (recommended for development)** — Installs from the local source code. Changes you make are reflected immediately without reinstalling.
> - **Option B: PyPI install** — Installs the latest published version from PyPI. Best if you just want to run samples without modifying the SDK.

**Option A: Local editable install (recommended for development):**
```bash
pip install -e .
pip install -r dev_requirements.txt
```

**Option B: PyPI install:**
```bash
pip install azure-ai-contentunderstanding
pip install -r dev_requirements.txt
```

This also installs all dependencies needed to run samples:
- `aiohttp` - Required for async operations
- `python-dotenv` - For loading `.env` files
- `azure-identity` - For `DefaultAzureCredential` authentication

> **[ASK USER] Installation check:**
> After running the install commands, ask: "Did the installation complete without errors?" If the user reports errors (e.g., permission issues, missing Python headers), help troubleshoot before continuing.

### Step 4: Configure Environment Variables

#### 4.1 Copy env.sample to .env (with safety check)

**Important:** This step copies the template without overwriting any existing `.env` file.

```bash
if [ -f ".env" ]; then
    echo "WARNING: .env file already exists - NOT overwriting"
    echo "If you want to start fresh, manually delete .env first: rm .env"
else
    cp env.sample .env
    echo "Created .env from env.sample"
    echo "Please edit .env and configure the required variables (see Step 4.2)"
fi
```

**For Windows PowerShell:**
```powershell
if (Test-Path ".env") {
    Write-Host "WARNING: .env file already exists - NOT overwriting"
    Write-Host "If you want to start fresh, manually delete .env first: Remove-Item .env"
} else {
    Copy-Item env.sample .env
    Write-Host "Created .env from env.sample"
    Write-Host "Please edit .env and configure the required variables (see Step 4.2)"
}
```

> **[ASK USER] Existing .env:**
> If a `.env` file already exists, ask: "A `.env` file already exists. Would you like to **keep** the existing one, or **start fresh** by deleting it and copying from `env.sample`?"

#### 4.2 Configure Required Variables

> **[ASK USER] Authentication method:**
> Ask the user: "How would you like to **authenticate** with Azure?"
> - **Option A: API Key** — You'll need your `CONTENTUNDERSTANDING_KEY` from the Azure Portal.
> - **Option B: DefaultAzureCredential (recommended)** — Uses `az login` or managed identity. No API key needed.
>
> Based on their choice, guide accordingly below.

> **[ASK USER] Provide endpoint:**
> Ask the user: "Please provide your **Microsoft Foundry endpoint URL**."
> - It should look like: `https://<your-resource-name>.services.ai.azure.com/`
> - Validate: it should NOT include `api-version` or other query parameters.
> - If the user doesn't know where to find it: direct them to Azure Portal → Their Foundry resource → Keys and Endpoint.

> **[ASK USER] Provide API key (if Option A):**
> If the user chose API Key authentication, ask: "Please provide your **API key** (`CONTENTUNDERSTANDING_KEY`)."
> - Found at: Azure Portal → Your Foundry resource → Keys and Endpoint → Key1 or Key2.
>
> If the user chose DefaultAzureCredential, remind them: "Make sure you've run `az login` to authenticate."

Open `.env` in your editor and set the following **required** variables:

| Variable | Description | How to Get It |
|----------|-------------|---------------|
| `CONTENTUNDERSTANDING_ENDPOINT` | Your Microsoft Foundry endpoint URL | Azure Portal → Your Foundry resource → Keys and Endpoint |
| `CONTENTUNDERSTANDING_KEY` | API key (optional if using DefaultAzureCredential) | Azure Portal → Your Foundry resource → Keys and Endpoint → Key1 or Key2 |

**For running `sample_update_defaults.py` (one-time model configuration):**

> **[ASK USER] Model deployment names:**
> Ask the user: "Do you want to configure **model deployment names** now? These are needed for `sample_update_defaults.py` (one-time setup)."
> - If yes, ask for each deployment name one by one with sensible defaults:
>   - "What is your **GPT-4.1** deployment name?" (default: `gpt-4.1`)
>   - "What is your **GPT-4.1-mini** deployment name?" (default: `gpt-4.1-mini`)
>   - "What is your **text-embedding-3-large** deployment name?" (default: `text-embedding-3-large`)
> - If no, let them know they can configure these later before running `sample_update_defaults.py`.

| Variable | Description | How to Get It |
|----------|-------------|---------------|
| `GPT_4_1_DEPLOYMENT` | Your GPT-4.1 deployment name | Microsoft Foundry → Deployments → Your GPT-4.1 deployment name |
| `GPT_4_1_MINI_DEPLOYMENT` | Your GPT-4.1-mini deployment name | Microsoft Foundry → Deployments → Your GPT-4.1-mini deployment name |
| `TEXT_EMBEDDING_3_LARGE_DEPLOYMENT` | Your text-embedding-3-large deployment name | Microsoft Foundry → Deployments → Your embedding deployment name |

#### 4.3 Validate Your Configuration

> **[ASK USER] Validate configuration:**
> After the user has provided all values, summarize the configuration and ask them to confirm:
> ```
> Here's your configuration:
>   CONTENTUNDERSTANDING_ENDPOINT = <value>
>   Authentication: API Key / DefaultAzureCredential
>   GPT_4_1_DEPLOYMENT = <value>
>   GPT_4_1_MINI_DEPLOYMENT = <value>
>   TEXT_EMBEDDING_3_LARGE_DEPLOYMENT = <value>
>
> Does this look correct? (Yes / No — let me fix something)
> ```
> Only write to `.env` after the user confirms.

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

> **[NOTE]:** Only guide the user through this step if they indicated during the prerequisites check that they do NOT yet have a Microsoft Foundry resource. Otherwise, skip to Step 6.

If you haven't set up your Microsoft Foundry resource yet:

#### 5.1 Create Microsoft Foundry Resource

1. Go to [Azure Portal](https://portal.azure.com/)
2. Create a **Microsoft Foundry resource** in a [supported region](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support)
3. Navigate to **Resource Management** > **Keys and Endpoint**
4. Copy the **Endpoint** URL and optionally a **Key**

> **[ASK USER] Resource created:**
> After guiding the user to create the resource, ask: "Have you created the Microsoft Foundry resource? Please share the **endpoint URL** so we can continue with configuration."

#### 5.2 Grant Cognitive Services User Role

This role is required even if you own the resource:

1. In your Foundry resource, go to **Access Control (IAM)**
2. Click **Add** > **Add role assignment**
3. Select **Cognitive Services User** role
4. Assign it to yourself

> **[ASK USER] Role assigned:**
> Ask: "Have you assigned the **Cognitive Services User** role to yourself? This is required even if you own the resource."

#### 5.3 Deploy Required Models

| Analyzer Type | Required Models |
|--------------|-----------------|
| `prebuilt-documentSearch`, `prebuilt-imageSearch`, `prebuilt-audioSearch`, `prebuilt-videoSearch` | gpt-4.1-mini, text-embedding-3-large |
| Other prebuilt analyzers (invoice, receipt, etc.) | gpt-4.1, text-embedding-3-large |

**To deploy a model:**
1. In Microsoft Foundry → **Deployments** → **Deploy model** → **Deploy base model**
2. Search and deploy: `gpt-4.1`, `gpt-4.1-mini`, `text-embedding-3-large`
3. Note deployment names (recommendation: use model name as deployment name)

> **[ASK USER] Models deployed:**
> Ask: "Have you deployed the required models? Please provide the **deployment names** you used for each:"
> - GPT-4.1 deployment name
> - GPT-4.1-mini deployment name
> - text-embedding-3-large deployment name
>
> Use these names to populate the `.env` file.

### Step 6: Configure Model Defaults (One-Time Setup)

> **[ASK USER] Run model defaults?:**
> Ask: "Would you like to run `sample_update_defaults.py` now to configure model defaults? This is a **one-time setup** per Microsoft Foundry resource. (Yes / Skip for now)"
> - If yes, ensure deployment name env vars are set, then run the script.
> - If no, let them know they'll need to run it before using prebuilt analyzers.

Run the configuration script to map deployed models to prebuilt analyzers:

```bash
cd samples
python sample_update_defaults.py
```

This is a **one-time setup per Microsoft Foundry resource**.

### Step 7: Run Samples

> **[ASK USER] Which samples?:**
> Ask: "Which sample would you like to run first?" with options:
> - `sample_analyze_url.py` — Analyze content from a URL (recommended start)
> - `sample_analyze_binary.py` — Analyze a local file
> - `sample_analyze_invoice.py` — Extract invoice fields
> - Other — Let me see the full list
> - Skip — I'll run samples on my own later
>
> If the user picks "Other", list available samples from the `samples/` directory.

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

> **[ASK USER] Sample result:**
> After running a sample, ask: "Did the sample run successfully? Would you like to run another sample or are you all set?"

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
    echo "Created .env - Please edit and configure required variables"
else
    echo "WARNING: .env already exists - skipping copy"
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
