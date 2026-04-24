#!/bin/bash
# Setup script for Azure AI Content Understanding SDK users
# This script sets up the environment for running samples

set -e

# Determine script directory and package root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

echo "=== Azure AI Content Understanding - User Environment Setup ==="
echo "Package root: $PACKAGE_ROOT"
echo ""

cd "$PACKAGE_ROOT"

# Step 0: Prerequisites check (Python 3.9+ with venv + pip)
echo "Step 0: Checking Python prerequisites..."
PY_CMD=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PY_CMD="$candidate"
        break
    fi
done
if [ -z "$PY_CMD" ]; then
    echo "  ✗ Python not found on PATH."
    echo "    Install Python 3.9+ then re-run this script:"
    echo "      Debian/Ubuntu: sudo apt install python3.12 python3.12-venv"
    echo "      macOS:         brew install python@3.12"
    exit 1
fi
py_version=$("$PY_CMD" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo "0.0")
py_major=${py_version%%.*}
py_minor=${py_version##*.}
if [ "$py_major" -lt 3 ] || { [ "$py_major" -eq 3 ] && [ "$py_minor" -lt 9 ]; }; then
    echo "  ✗ Found Python $py_version via '$PY_CMD', need 3.9+."
    echo "    Debian/Ubuntu: sudo apt install python3.12 python3.12-venv"
    echo "    macOS:         brew install python@3.12"
    exit 1
fi
if ! "$PY_CMD" -c 'import venv' >/dev/null 2>&1; then
    echo "  ✗ '$PY_CMD' cannot 'import venv' (python3.x-venv package missing)."
    echo "    Debian/Ubuntu: sudo apt install python${py_version}-venv"
    exit 1
fi
if ! "$PY_CMD" -m pip --version >/dev/null 2>&1; then
    echo "  ✗ pip not available for '$PY_CMD'. Install via your package manager and retry."
    exit 1
fi
echo "  ✓ $PY_CMD $py_version (venv + pip OK)"
echo ""

# Step 1: Check and create virtual environment
echo "Step 1: Checking virtual environment..."
if [ -d ".venv" ]; then
    echo "  ✓ Virtual environment already exists at .venv"
else
    echo "  Creating virtual environment..."
    "$PY_CMD" -m venv .venv
    echo "  ✓ Virtual environment created at .venv"
fi
echo ""

# Step 2: Activate virtual environment
echo "Step 2: Activating virtual environment..."
source .venv/bin/activate
echo "  ✓ Virtual environment activated"
echo "  Python: $(which python)"
echo ""

# Step 3: Install SDK and dependencies
echo "Step 3: Installing SDK and dependencies..."
echo "  Installing azure-ai-contentunderstanding..."
pip install azure-ai-contentunderstanding --quiet
echo "  Installing sample dependencies..."
pip install -r dev_requirements.txt --quiet
echo "  ✓ Dependencies installed"
echo ""

# Step 4: Configure environment file
echo "Step 4: Configuring environment file..."
if [ -f ".env" ]; then
    echo "  ⚠ .env file already exists - NOT overwriting"
    echo "  If you want to start fresh, delete .env manually: rm .env"
else
    if [ -f "env.sample" ]; then
        cp env.sample .env
        echo "  ✓ Created .env from env.sample"
    else
        echo "  ⚠ env.sample not found, skipping .env creation"
    fi
fi
echo ""

# Step 5: Check and prompt for required configuration
echo "Step 5: Environment variable configuration..."
echo ""
echo "  Required variables for running samples:"
echo "  ┌─────────────────────────────────────────────────────────────────┐"
echo "  │ CONTENTUNDERSTANDING_ENDPOINT - Your Microsoft Foundry endpoint│"
echo "  │   Example: https://my-resource.services.ai.azure.com/          │"
echo "  │                                                                 │"
echo "  │ CONTENTUNDERSTANDING_KEY - API key (optional)                  │"
echo "  │   If not set, DefaultAzureCredential is used (run 'az login')  │"
echo "  └─────────────────────────────────────────────────────────────────┘"
echo ""
echo "  Required for sample_update_defaults.py (one-time model config):"
echo "  ┌─────────────────────────────────────────────────────────────────┐"
echo "  │ GPT_4_1_DEPLOYMENT              - Your GPT-4.1 deployment name │"
echo "  │ GPT_4_1_MINI_DEPLOYMENT         - Your GPT-4.1-mini deployment │"
echo "  │ TEXT_EMBEDDING_3_LARGE_DEPLOYMENT - Your embedding deployment  │"
echo "  └─────────────────────────────────────────────────────────────────┘"
echo ""

# Ask if user wants to configure now
read -p "Would you like to configure required variables now? (y/N): " configure_now
if [[ "$configure_now" =~ ^[Yy]$ ]]; then
    echo ""
    
    # CONTENTUNDERSTANDING_ENDPOINT
    read -p "Enter CONTENTUNDERSTANDING_ENDPOINT (e.g., https://my-resource.services.ai.azure.com/): " endpoint
    if [ -n "$endpoint" ]; then
        # Use | as delimiter to avoid issues with URLs containing /
        sed -i "s|CONTENTUNDERSTANDING_ENDPOINT=.*|CONTENTUNDERSTANDING_ENDPOINT=$endpoint|" .env
        echo "  ✓ Set CONTENTUNDERSTANDING_ENDPOINT"
    else
        echo "  ⚠ Skipped CONTENTUNDERSTANDING_ENDPOINT (required - please set manually)"
    fi
    
    # CONTENTUNDERSTANDING_KEY
    read -p "Enter CONTENTUNDERSTANDING_KEY (press Enter to use DefaultAzureCredential): " api_key
    if [ -n "$api_key" ]; then
        sed -i "s|CONTENTUNDERSTANDING_KEY=.*|CONTENTUNDERSTANDING_KEY=$api_key|" .env
        echo "  ✓ Set CONTENTUNDERSTANDING_KEY"
    else
        echo "  ℹ Using DefaultAzureCredential - make sure to run 'az login'"
    fi

    # Probe existing model defaults on the Foundry resource before prompting.
    # Exit codes from the probe:
    #   0  ALL_SET   - all 3 deployments already mapped
    #   10 PARTIAL   - some mapped, some missing
    #   2  NONE      - no defaults configured
    #   3  AUTH      - 401/403 authentication error
    #   1  OTHER     - any other error (DNS, SDK, etc.)
    gpt41=""
    gpt41mini=""
    embedding=""
    probe_rc=1
    probe_out=""
    if [ -n "$endpoint" ]; then
        echo ""
        echo "  Probing existing model defaults on the Foundry resource..."
        probe_out="$(
            CONTENTUNDERSTANDING_ENDPOINT="$endpoint" \
            CONTENTUNDERSTANDING_KEY="$api_key" \
            python - <<'PY' 2>/dev/null
import os, sys
try:
    from azure.ai.contentunderstanding import ContentUnderstandingClient
    from azure.core.credentials import AzureKeyCredential
    from azure.identity import DefaultAzureCredential
    from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
except Exception:
    sys.exit(1)
ep = os.environ.get("CONTENTUNDERSTANDING_ENDPOINT", "")
key = os.environ.get("CONTENTUNDERSTANDING_KEY") or None
if not ep:
    sys.exit(1)
cred = AzureKeyCredential(key) if key else DefaultAzureCredential()
try:
    d = ContentUnderstandingClient(ep, cred).get_defaults().model_deployments or {}
except ClientAuthenticationError:
    sys.exit(3)
except HttpResponseError as e:
    sys.exit(3 if e.status_code in (401, 403) else 1)
except Exception:
    sys.exit(1)
keys = ["gpt-4.1", "gpt-4.1-mini", "text-embedding-3-large"]
vals = [d.get(k, "") for k in keys]
print(";".join(f"{k}={v}" for k, v in zip(keys, vals)))
sys.exit(0 if all(vals) else (2 if not any(vals) else 10))
PY
        )"
        probe_rc=$?

        # Parse probe output (K=V;K=V;K=V) when useful
        if [ "$probe_rc" = "0" ] || [ "$probe_rc" = "10" ]; then
            gpt41="$(    echo "$probe_out" | tr ';' '\n' | sed -n 's/^gpt-4\.1=//p' | head -n1)"
            gpt41mini="$(echo "$probe_out" | tr ';' '\n' | sed -n 's/^gpt-4\.1-mini=//p' | head -n1)"
            embedding="$( echo "$probe_out" | tr ';' '\n' | sed -n 's/^text-embedding-3-large=//p' | head -n1)"
        fi

        case "$probe_rc" in
            0)
                echo "  ✓ Detected existing defaults:"
                echo "      gpt-4.1                = $gpt41"
                echo "      gpt-4.1-mini           = $gpt41mini"
                echo "      text-embedding-3-large = $embedding"
                read -p "  Use these detected values? (Y/n): " use_detected
                if [[ ! "$use_detected" =~ ^[Nn]$ ]]; then
                    skip_update_defaults=1
                else
                    gpt41=""; gpt41mini=""; embedding=""
                fi
                ;;
            10)
                echo "  ℹ Partial defaults detected; missing entries will be prompted below."
                ;;
            2)
                echo "  ℹ No existing defaults detected; continuing with manual entry."
                ;;
            3)
                echo "  ⚠ Probe unavailable (authentication failed)."
                echo "    If you're using DefaultAzureCredential, run 'az login' and ensure"
                echo "    the Cognitive Services User role is assigned. Continuing with manual entry."
                ;;
            *)
                echo "  ⚠ Probe failed (exit=$probe_rc); continuing with manual entry."
                ;;
        esac
    fi

    echo ""
    echo "  Model deployment configuration (for sample_update_defaults.py):"

    # GPT_4_1_DEPLOYMENT
    if [ -z "$gpt41" ]; then
        read -p "Enter GPT_4_1_DEPLOYMENT (default: gpt-4.1): " gpt41
        gpt41="${gpt41:-gpt-4.1}"
    else
        echo "  ✓ Using detected GPT_4_1_DEPLOYMENT=$gpt41"
    fi
    sed -i "s|GPT_4_1_DEPLOYMENT=.*|GPT_4_1_DEPLOYMENT=$gpt41|" .env

    # GPT_4_1_MINI_DEPLOYMENT
    if [ -z "$gpt41mini" ]; then
        read -p "Enter GPT_4_1_MINI_DEPLOYMENT (default: gpt-4.1-mini): " gpt41mini
        gpt41mini="${gpt41mini:-gpt-4.1-mini}"
    else
        echo "  ✓ Using detected GPT_4_1_MINI_DEPLOYMENT=$gpt41mini"
    fi
    sed -i "s|GPT_4_1_MINI_DEPLOYMENT=.*|GPT_4_1_MINI_DEPLOYMENT=$gpt41mini|" .env

    # TEXT_EMBEDDING_3_LARGE_DEPLOYMENT
    if [ -z "$embedding" ]; then
        read -p "Enter TEXT_EMBEDDING_3_LARGE_DEPLOYMENT (default: text-embedding-3-large): " embedding
        embedding="${embedding:-text-embedding-3-large}"
    else
        echo "  ✓ Using detected TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=$embedding"
    fi
    sed -i "s|TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=.*|TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=$embedding|" .env

    echo ""
    echo "  ✓ Environment variables configured"
else
    echo ""
    echo "  Please edit .env manually with your configuration:"
    echo "    nano .env"
    echo "  or"
    echo "    code .env"
fi
echo ""

# Summary
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo ""
echo "  1. Activate virtual environment (in new terminals):"
echo "     cd $PACKAGE_ROOT"
echo "     source .venv/bin/activate"
echo ""
if [ "${skip_update_defaults:-0}" = "1" ]; then
    echo "  2. Model defaults already configured on your Foundry resource; skip sample_update_defaults.py."
else
    echo "  2. Configure model defaults (one-time per Foundry resource):"
    echo "     cd samples"
    echo "     python sample_update_defaults.py"
fi
echo ""
echo "  3. Run samples:"
echo "     python sample_analyze_url.py"
echo "     python sample_analyze_binary.py"
echo ""
