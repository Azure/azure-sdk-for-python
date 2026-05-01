#!/bin/bash
# Setup script for Azure AI Content Understanding SDK users
# This script sets up the environment for running samples
# cspell:ignore pyver esac

set -e

# Determine script directory and package root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

echo "=== Azure AI Content Understanding - User Environment Setup ==="
echo "Package root: $PACKAGE_ROOT"
echo ""

cd "$PACKAGE_ROOT"

# --- helper: offer to install Python via the platform's package manager --------
# Usage: offer_install_python <reason> [<py_version>]
#   reason: "missing" | "too_old" | "no_venv"
# Returns 0 if install ran successfully (caller should re-probe), non-zero if
# the user declined, the platform isn't supported, or the install failed.
offer_install_python() {
    local reason="$1"
    local pyver="${2:-}"
    local os_name
    os_name="$(uname -s)"
    local cmd=""
    case "$os_name" in
        Darwin)
            if ! command -v brew >/dev/null 2>&1; then
                echo "    (Homebrew not found — install it first: https://brew.sh/)"
                return 1
            fi
            cmd="brew install python@3.12"
            ;;
        Linux)
            if ! command -v apt-get >/dev/null 2>&1; then
                echo "    (No apt-get detected — install Python 3.9+ with your distro's package manager.)"
                return 1
            fi
            if [ "$reason" = "no_venv" ] && [ -n "$pyver" ]; then
                cmd="sudo apt-get update && sudo apt-get install -y python${pyver}-venv"
            else
                cmd="sudo apt-get update && sudo apt-get install -y python3.12 python3.12-venv"
            fi
            ;;
        *)
            echo "    (Unsupported platform for auto-install: $os_name)"
            return 1
            ;;
    esac
    echo ""
    echo "  This script can run the following command for you:"
    echo "    $cmd"
    local reply=""
    read -r -p "  Run it now? (y/N): " reply || reply="n"
    if [[ ! "$reply" =~ ^[Yy]$ ]]; then
        echo "  Please run it yourself, then re-run this script."
        return 1
    fi
    if ! eval "$cmd"; then
        echo "  ✗ Installation command failed."
        return 1
    fi
    echo "  ✓ Installation complete. Re-probing..."
    hash -r 2>/dev/null || true
    return 0
}

# Step 0: Prerequisites check (Python 3.9+ with venv + pip)
echo "Step 0: Checking Python prerequisites..."
attempt=1
while :; do
    PY_CMD=""
    for candidate in python3.12 python3 python; do
        if command -v "$candidate" >/dev/null 2>&1; then
            PY_CMD="$candidate"
            break
        fi
    done

    fail_reason=""
    py_version=""
    if [ -z "$PY_CMD" ]; then
        echo "  ✗ Python not found on PATH."
        fail_reason="missing"
    else
        py_version=$("$PY_CMD" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo "0.0")
        py_major=${py_version%%.*}
        py_minor=${py_version##*.}
        if [ "$py_major" -lt 3 ] || { [ "$py_major" -eq 3 ] && [ "$py_minor" -lt 9 ]; }; then
            echo "  ✗ Found Python $py_version via '$PY_CMD', need 3.9+."
            fail_reason="too_old"
        elif ! "$PY_CMD" -c 'import venv' >/dev/null 2>&1; then
            echo "  ✗ '$PY_CMD' cannot 'import venv' (python3.x-venv package missing)."
            fail_reason="no_venv"
        elif ! "$PY_CMD" -m pip --version >/dev/null 2>&1; then
            echo "  ✗ pip not available for '$PY_CMD'. Install via your package manager and retry."
            exit 1
        fi
    fi

    if [ -z "$fail_reason" ]; then
        echo "  ✓ $PY_CMD $py_version (venv + pip OK)"
        break
    fi

    if [ "$attempt" -ge 2 ]; then
        echo "  ✗ Python prerequisites still not satisfied after install attempt. Aborting."
        exit 1
    fi
    if ! offer_install_python "$fail_reason" "$py_version"; then
        exit 1
    fi
    attempt=$((attempt + 1))
done
echo ""

# Step 1: Check and create virtual environment
echo "Step 1: Checking virtual environment..."
if [ -d ".venv" ]; then
    venv_py=".venv/bin/python"
    current_version="$py_version"
    venv_version=""
    if [ ! -x "$venv_py" ]; then
        echo "  ⚠ Existing .venv is missing its Python interpreter; recreating..."
        rm -rf .venv
    else
        venv_version="$($venv_py -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo "unknown")"
        if [ "$venv_version" != "$current_version" ]; then
            echo "  ⚠ Existing .venv uses Python $venv_version but current interpreter is $current_version; recreating..."
            rm -rf .venv
        else
            echo "  ✓ Virtual environment already exists at .venv"
        fi
    fi
else
    echo "  Creating virtual environment..."
    "$PY_CMD" -m venv .venv
    echo "  ✓ Virtual environment created at .venv"
fi
if [ ! -d ".venv" ]; then
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

deps_installed() {
    python - <<'PY' >/dev/null 2>&1
required = [
    "azure.ai.contentunderstanding",
    "azure.identity",
    "azure.storage.blob",
    "aiohttp",
    "dotenv",
    "devtools_testutils",
]
for module_name in required:
    __import__(module_name)
PY
}

# Step 3: Install SDK and dependencies
echo "Step 3: Installing SDK and dependencies..."
if deps_installed; then
    echo "  ✓ Required SDK dependencies already installed; skipping pip install"
else
    install_mode="pypi"
    read -r -p "  Install from PyPI [P] or local editable install [E]? (P/e): " mode_choice || mode_choice=""
    if [[ "$mode_choice" =~ ^[Ee]$ ]]; then
        install_mode="editable"
    fi

    if [ "$install_mode" = "editable" ]; then
        echo "  Installing azure-ai-contentunderstanding (editable)..."
        if ! python -m pip install -e . --quiet; then
            echo "  ✗ pip install -e . failed."
            exit 1
        fi
    else
        echo "  Installing azure-ai-contentunderstanding (PyPI)..."
        if ! python -m pip install azure-ai-contentunderstanding --quiet; then
            echo "  ✗ pip install azure-ai-contentunderstanding failed."
            exit 1
        fi
    fi
    echo "  Installing sample dependencies..."
    if ! python -m pip install -r dev_requirements.txt --quiet; then
        echo "  ✗ pip install -r dev_requirements.txt failed."
        exit 1
    fi
    echo "  ✓ Dependencies installed"
fi
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
read -r -p "Would you like to configure required variables now? (y/N): " configure_now || configure_now="n"
if [[ "$configure_now" =~ ^[Yy]$ ]]; then
    echo ""

    # Detect sed in-place flag once (macOS BSD sed requires -i '', GNU sed uses -i)
    if sed --version 2>/dev/null | grep -q GNU; then
        SED_INPLACE=(sed -i)
    else
        SED_INPLACE=(sed -i '')
    fi
    
    # CONTENTUNDERSTANDING_ENDPOINT
    read -r -p "Enter CONTENTUNDERSTANDING_ENDPOINT (e.g., https://my-resource.services.ai.azure.com/): " endpoint || endpoint=""
    if [ -n "$endpoint" ]; then
        # Use | as delimiter to avoid issues with URLs containing /
        "${SED_INPLACE[@]}" "s|CONTENTUNDERSTANDING_ENDPOINT=.*|CONTENTUNDERSTANDING_ENDPOINT=$endpoint|" .env
        echo "  ✓ Set CONTENTUNDERSTANDING_ENDPOINT"
    else
        echo "  ⚠ Skipped CONTENTUNDERSTANDING_ENDPOINT (required - please set manually)"
    fi
    
    # CONTENTUNDERSTANDING_KEY
    read -r -p "Enter CONTENTUNDERSTANDING_KEY (press Enter to use DefaultAzureCredential): " api_key || api_key=""
    if [ -n "$api_key" ]; then
        "${SED_INPLACE[@]}" "s|CONTENTUNDERSTANDING_KEY=.*|CONTENTUNDERSTANDING_KEY=$api_key|" .env
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
        # Temporarily disable set -e: probe exit codes 2/3/10 are expected
        # non-zero values; we capture them in probe_rc.
        set +e
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
        set -e

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
                read -r -p "  Use these detected values? (Y/n): " use_detected || use_detected="y"
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
        read -r -p "Enter GPT_4_1_DEPLOYMENT (default: gpt-4.1): " gpt41 || gpt41=""
        gpt41="${gpt41:-gpt-4.1}"
    else
        echo "  ✓ Using detected GPT_4_1_DEPLOYMENT=$gpt41"
    fi
    "${SED_INPLACE[@]}" "s|GPT_4_1_DEPLOYMENT=.*|GPT_4_1_DEPLOYMENT=$gpt41|" .env

    # GPT_4_1_MINI_DEPLOYMENT
    if [ -z "$gpt41mini" ]; then
        read -r -p "Enter GPT_4_1_MINI_DEPLOYMENT (default: gpt-4.1-mini): " gpt41mini || gpt41mini="" gpt41mini
        gpt41mini="${gpt41mini:-gpt-4.1-mini}"
    else
        echo "  ✓ Using detected GPT_4_1_MINI_DEPLOYMENT=$gpt41mini"
    fi
    "${SED_INPLACE[@]}" "s|GPT_4_1_MINI_DEPLOYMENT=.*|GPT_4_1_MINI_DEPLOYMENT=$gpt41mini|" .env

    # TEXT_EMBEDDING_3_LARGE_DEPLOYMENT
    if [ -z "$embedding" ]; then
        read -r -p "Enter TEXT_EMBEDDING_3_LARGE_DEPLOYMENT (default: text-embedding-3-large): " embedding || embedding=""
        embedding="${embedding:-text-embedding-3-large}"
    else
        echo "  ✓ Using detected TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=$embedding"
    fi
    "${SED_INPLACE[@]}" "s|TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=.*|TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=$embedding|" .env

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
