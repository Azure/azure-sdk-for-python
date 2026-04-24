---
name: cu-sdk-setup
description: Guide SDK users through setting up their Python environment for Azure AI Content Understanding. Use this skill when users need help installing the SDK, configuring Azure resources, deploying required models, setting environment variables, or running samples.
---

# SDK User Environment Setup for Azure AI Content Understanding

Set up your Python environment to use the Azure AI Content Understanding SDK and run samples.

> **[COPILOT INTERACTION MODEL]:** This skill is designed to be interactive. At each step marked with **[ASK USER]**, pause execution and prompt the user for input or confirmation before proceeding. Do NOT silently skip these prompts. Use the `ask_questions` tool when available.

## Prerequisites

Before starting, ensure you have:

- **Python 3.9 or later** installed
- An **Azure subscription** ([create one for free](https://azure.microsoft.com/free/))
- A **Microsoft Foundry resource** in a [supported region](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support)

> **[COPILOT] Probe Python runtime first (before asking):**
> Do not take the user's word for it — run these checks, then report. This prevents silent failures later in `python -m venv`.
>
> ```bash
> # POSIX / WSL / macOS
> python3 --version 2>/dev/null || python --version 2>/dev/null
> python3 -m pip --version 2>/dev/null || python -m pip --version 2>/dev/null
> python3 -c "import venv" 2>/dev/null && echo "venv: ok" || echo "venv: MISSING"
> ```
>
> ```powershell
> # Windows PowerShell
> py -3 --version 2>$null; if ($LASTEXITCODE -ne 0) { python --version }
> py -3 -m pip --version 2>$null
> py -3 -c "import venv" 2>$null; if ($LASTEXITCODE -eq 0) { 'venv: ok' } else { 'venv: MISSING' }
> ```
>
> **Decision table:**
>
> | Finding | Action |
> |---|---|
> | `Python 3.9+` and `venv: ok` and `pip` present | ✓ Good to go. Proceed to Step 1. |
> | Python missing or `< 3.9` | Report the finding, then go to the **[ASK USER] Python install choice** block below. |
> | `venv: MISSING` (common on Debian/Ubuntu base images) | Report the finding, then go to the **[ASK USER] Python install choice** block below. |
> | Windows resolves to a `WindowsApps\python*.exe` stub | Report the finding, then go to the **[ASK USER] Python install choice** block below (auto-install cannot fix this — user must disable App Execution Aliases). |
>
> **[ASK USER] Python install choice (only when probe fails):**
> Ask the user: "Python is missing / too old / the `venv` module is unavailable. How would you like to proceed?"
> - **Option A: Install it for me** — Agent runs the platform-appropriate install command (see below), verifies, and continues. Requires elevated privileges on Linux (`sudo`). Not available for the Windows App Execution Alias case — that requires manual UI action.
> - **Option B: I'll install it myself** — Agent prints the install command for the user's platform and stops. User runs it, re-opens the terminal, and tells the agent to resume.
>
> **Default install commands (Option A):**
> - **macOS** → `brew install python@3.12` (requires Homebrew; if not installed, fall back to Option B)
> - **Debian / Ubuntu / WSL** → `sudo apt update && sudo apt install -y python3.12 python3.12-venv` (will prompt for sudo password)
> - **Debian / Ubuntu — `venv: MISSING` only** → `sudo apt install -y python3-venv` (matches the existing Python version)
> - **Windows** → `winget install Python.Python.3.12` (run in an elevated PowerShell if needed)
>
> **Before running Option A, confirm with the user one more time** by restating the exact command that will execute, then proceed. After install, re-run the probe to verify `Python 3.9+` and `venv: ok` before continuing.
>
> **Windows gotcha — App Execution Aliases:** Even after uninstalling the Store Python stub, the `python.exe` / `python3.exe` entries under `C:\Users\<you>\AppData\Local\Microsoft\WindowsApps\` may persist as **App Execution Aliases** and shadow a real install. If the probe still reports a stub after the user confirms they installed real Python:
>   1. Point them to **Settings → Apps → Advanced app settings → App execution aliases**, and toggle **off** `python.exe` and `python3.exe`.
>   2. As a fallback, suggest invoking Python via the `py` launcher (`py -3 -m venv .venv`) or the explicit install path (e.g. `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`). The companion `setup_user_env.ps1` script already probes well-known install paths automatically.
>
> Report the detected version + venv status back to the user in one sentence before the `[ASK USER]` block below.

> **[ASK USER] Prerequisites Check:**
> After the probe above, confirm the remaining items:
> 1. "Do you already have a **Microsoft Foundry resource** set up in Azure?" — If no, jump to **Step 5** (Azure Resource Setup) first, then return here.
> 2. "Have you already deployed the required **AI models** (GPT-4.1, GPT-4.1-mini, text-embedding-3-large) in Microsoft Foundry?" — If no, include Step 5.3 and Step 6 in the workflow.

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

> **[COPILOT] Existing `.venv` behavior:**
> If `.venv` already exists, prefer reusing it. If the existing virtual environment was created with a different Python minor version than the interpreter selected in the prerequisite probe, or if the environment is incomplete/corrupted, recreate `.venv` before continuing. This avoids subtle failures when the machine later upgrades from one supported Python version to another (for example, 3.9 → 3.12).

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
> - **Option A: PyPI install (recommended)** — Installs the latest published version from PyPI. Best for running samples and developing Content Understanding-based solutions using the SDK.
> - **Option B: Local editable install (for SDK contribution)** — Use this only when you are contributing to the Content Understanding SDK. Installs from local source code; changes are reflected immediately without reinstalling.

**Option A: PyPI install (recommended):**
```bash
pip install azure-ai-contentunderstanding
pip install -r dev_requirements.txt
```

**Option B: Local editable install (for Content Understanding SDK contribution):**
```bash
pip install -e .
pip install -r dev_requirements.txt
```

> **[COPILOT] Repeated-run behavior:**
> On repeated runs, if the required SDK/sample dependencies are already importable from the active virtual environment, the setup scripts may skip the `pip install` step instead of reinstalling everything. Only rerun the install commands when dependencies are missing or the virtual environment was recreated.

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

> **[COPILOT] Probe existing model defaults on the Foundry resource:**
> Before asking the user for deployment names, probe what the resource already has configured. The venv is active and the SDK is installed, so call `get_defaults()` via a short inline Python snippet. Export `CONTENTUNDERSTANDING_ENDPOINT` (and `CONTENTUNDERSTANDING_KEY` if Option A) in the shell first so the snippet can read them.
>
> ```bash
> python - <<'PY'
> import os, sys
> from azure.ai.contentunderstanding import ContentUnderstandingClient
> from azure.core.credentials import AzureKeyCredential
> from azure.identity import DefaultAzureCredential
> from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
>
> ep = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
> key = os.environ.get("CONTENTUNDERSTANDING_KEY") or None
> cred = AzureKeyCredential(key) if key else DefaultAzureCredential()
> try:
>     d = ContentUnderstandingClient(ep, cred).get_defaults().model_deployments or {}
> except ClientAuthenticationError:
>     sys.exit(3)
> except HttpResponseError as e:
>     sys.exit(3 if e.status_code in (401, 403) else 1)
> except Exception:
>     sys.exit(1)
>
> keys = ["gpt-4.1", "gpt-4.1-mini", "text-embedding-3-large"]
> vals = [d.get(k, "") for k in keys]
> print(";".join(f"{k}={v}" for k, v in zip(keys, vals)))
> sys.exit(0 if all(vals) else (2 if not any(vals) else 10))
> PY
> ```
>
> Branch on the exit code:
>
> | Exit | Meaning | Action |
> |------|---------|--------|
> | `0` | **ALL_SET** — all 3 deployments already mapped on the resource | Show the detected values and ask *"Detected existing defaults: gpt-4.1=`<A>`, gpt-4.1-mini=`<B>`, text-embedding-3-large=`<C>`. Use these? (Y/n)"*. On Y, prefill the 3 env vars and **skip Step 6** (defaults already configured). On n, fall through to the per-model prompts below. |
> | `10` | **PARTIAL** — some mapped, some missing | Prefill the ones that are set. For missing models, ask per-item with the default shown below. After Step 4 completes, run Step 6 to fill the gaps. |
> | `2` | **NONE** — resource has no defaults yet | Fall through to the per-model prompts below. Step 6 will configure them. |
> | `3` | **AUTH_ERROR** (401/403) | Print a one-line warning: *"Probe unavailable (auth failed). If you're using DefaultAzureCredential, run `az login` and ensure the Cognitive Services User role is assigned. Continuing with manual entry."* Fall through to per-model prompts. |
> | other | Unexpected error | Print *"Probe failed: `<error>`. Continuing with manual entry."* Fall through. |
>
> Only proceed to the per-model prompts below when the probe outcome requires it.

> **[ASK USER] Model deployment names (only when probe did not yield all values):**
> For each model not already prefilled from the probe, ask with a sensible default:
>   - "What is your **GPT-4.1** deployment name?" (default: `gpt-4.1`)
>   - "What is your **GPT-4.1-mini** deployment name?" (default: `gpt-4.1-mini`)
>   - "What is your **text-embedding-3-large** deployment name?" (default: `text-embedding-3-large`)
>
> If the user prefers to configure these later, let them know they can run `sample_update_defaults.py` (Step 6) anytime before using prebuilt analyzers.

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
CONTENTUNDERSTANDING_KEY=

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

> **[COPILOT] Skip condition:**
> If the Step 4.2 probe returned **ALL_SET** and the user accepted the detected values, defaults are already configured on the Foundry resource — skip this step and tell the user *"Your Foundry resource already has model defaults configured; skipping Step 6."* Otherwise continue below.

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
> - `sample_analyze_binary.py` — Analyze a local PDF (quickest; completes in under a minute)
> - `sample_analyze_url.py` — Full demo: document + video + audio + image from URLs (runs several analyses; takes a few minutes, please be patient)
> - `sample_analyze_invoice.py` — Extract invoice fields
> - Other — Let me see the full list
> - Skip — I'll run samples on my own later
>
> If the user picks "Other", list available samples from the `samples/` directory.
>
> **[COPILOT] Timing note (do not parrot verbatim to user):** `sample_analyze_url.py` runs 14 sequential LROs (document + video + audio + image, with multiple content-range variants). Video/audio chapter generation is slow on the service side, so total runtime can be on the order of 15+ minutes today. Do not interpret quiet periods (no stdout for several minutes during a video/audio LRO) as a hang. Only consider killing if there is **no new stdout for 5+ minutes** AND no active HTTP traffic. When talking to the user, prefer phrasing like "takes a few minutes" or "please be patient" rather than citing exact large minute counts.

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
.github/skills/cu-sdk-setup/scripts/setup_user_env.sh
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

## Related Skills

- `cu-sdk-sample-run` - Run individual samples (including `sample_update_defaults` for model deployment setup)
- `cu-sdk-common-knowledge` - Domain knowledge for Content Understanding concepts

## Additional Resources

- [SDK README](../../../README.md) - Full documentation
- [Samples README](../../../samples/README.md) - Sample descriptions
- [Product Documentation](https://learn.microsoft.com/azure/ai-services/content-understanding/)
- [Prebuilt Analyzers](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers)
