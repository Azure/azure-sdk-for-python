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

# Step 1: Check and create virtual environment
echo "Step 1: Checking virtual environment..."
if [ -d ".venv" ]; then
    echo "  ✓ Virtual environment already exists at .venv"
else
    echo "  Creating virtual environment..."
    python3 -m venv .venv || python -m venv .venv
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
    
    echo ""
    echo "  Model deployment configuration (for sample_update_defaults.py):"
    
    # GPT_4_1_DEPLOYMENT
    read -p "Enter GPT_4_1_DEPLOYMENT (default: gpt-4.1): " gpt41
    gpt41="${gpt41:-gpt-4.1}"
    sed -i "s|GPT_4_1_DEPLOYMENT=.*|GPT_4_1_DEPLOYMENT=$gpt41|" .env
    echo "  ✓ Set GPT_4_1_DEPLOYMENT=$gpt41"
    
    # GPT_4_1_MINI_DEPLOYMENT
    read -p "Enter GPT_4_1_MINI_DEPLOYMENT (default: gpt-4.1-mini): " gpt41mini
    gpt41mini="${gpt41mini:-gpt-4.1-mini}"
    sed -i "s|GPT_4_1_MINI_DEPLOYMENT=.*|GPT_4_1_MINI_DEPLOYMENT=$gpt41mini|" .env
    echo "  ✓ Set GPT_4_1_MINI_DEPLOYMENT=$gpt41mini"
    
    # TEXT_EMBEDDING_3_LARGE_DEPLOYMENT
    read -p "Enter TEXT_EMBEDDING_3_LARGE_DEPLOYMENT (default: text-embedding-3-large): " embedding
    embedding="${embedding:-text-embedding-3-large}"
    sed -i "s|TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=.*|TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=$embedding|" .env
    echo "  ✓ Set TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=$embedding"
    
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
echo "  2. Configure model defaults (one-time per Foundry resource):"
echo "     cd samples"
echo "     python sample_update_defaults.py"
echo ""
echo "  3. Run samples:"
echo "     python sample_analyze_url.py"
echo "     python sample_analyze_binary.py"
echo ""
