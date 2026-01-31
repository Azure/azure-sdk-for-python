#!/bin/bash
# Setup script for azure-ai-contentunderstanding Python development environment
# This script sets up venv, installs dependencies, and configures environment variables

set -e

# Determine script directory and package root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

echo "=== Azure AI Content Understanding - Python Environment Setup ==="
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

# Step 3: Install dependencies
echo "Step 3: Installing dependencies..."
echo "  Installing package in editable mode..."
pip install -e . --quiet
echo "  Installing dev requirements..."
pip install -r dev_requirements.txt --quiet
echo "  ✓ Dependencies installed"
echo ""

# Step 4: Configure environment variables
echo "Step 4: Configuring environment variables..."
if [ -f ".env" ]; then
    echo "  ✓ .env file already exists"
else
    if [ -f "env.sample" ]; then
        cp env.sample .env
        echo "  ✓ Created .env from env.sample"
        echo ""
        echo "  ⚠ Please configure the required variables in .env:"
        echo ""
        echo "  Required variables:"
        echo "    CONTENTUNDERSTANDING_ENDPOINT - Your Microsoft Foundry endpoint URL"
        echo "    CONTENTUNDERSTANDING_KEY      - API key (optional if using DefaultAzureCredential)"
        echo ""
        echo "  For running sample_update_defaults.py:"
        echo "    GPT_4_1_DEPLOYMENT             - Your GPT-4.1 deployment name"
        echo "    GPT_4_1_MINI_DEPLOYMENT        - Your GPT-4.1-mini deployment name"
        echo "    TEXT_EMBEDDING_3_LARGE_DEPLOYMENT - Your text-embedding-3-large deployment name"
        echo ""
        
        # Ask user if they want to configure now
        read -p "  Would you like to configure required variables now? (y/N): " configure_now
        if [[ "$configure_now" =~ ^[Yy]$ ]]; then
            echo ""
            read -p "  Enter CONTENTUNDERSTANDING_ENDPOINT: " endpoint
            if [ -n "$endpoint" ]; then
                sed -i "s|CONTENTUNDERSTANDING_ENDPOINT=.*|CONTENTUNDERSTANDING_ENDPOINT=$endpoint|" .env
            fi
            
            read -p "  Enter CONTENTUNDERSTANDING_KEY (press Enter to skip for DefaultAzureCredential): " api_key
            if [ -n "$api_key" ]; then
                sed -i "s|CONTENTUNDERSTANDING_KEY=.*|CONTENTUNDERSTANDING_KEY=$api_key|" .env
            fi
            
            read -p "  Enter GPT_4_1_DEPLOYMENT (default: gpt-4.1): " gpt41
            gpt41="${gpt41:-gpt-4.1}"
            sed -i "s|GPT_4_1_DEPLOYMENT=.*|GPT_4_1_DEPLOYMENT=$gpt41|" .env
            
            read -p "  Enter GPT_4_1_MINI_DEPLOYMENT (default: gpt-4.1-mini): " gpt41mini
            gpt41mini="${gpt41mini:-gpt-4.1-mini}"
            sed -i "s|GPT_4_1_MINI_DEPLOYMENT=.*|GPT_4_1_MINI_DEPLOYMENT=$gpt41mini|" .env
            
            read -p "  Enter TEXT_EMBEDDING_3_LARGE_DEPLOYMENT (default: text-embedding-3-large): " embedding
            embedding="${embedding:-text-embedding-3-large}"
            sed -i "s|TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=.*|TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=$embedding|" .env
            
            echo ""
            echo "  ✓ Environment variables configured"
        fi
    else
        echo "  ⚠ env.sample not found, skipping .env creation"
    fi
fi
echo ""

# Summary
echo "=== Setup Complete ==="
echo ""
echo "To activate the virtual environment in a new terminal:"
echo "  cd $PACKAGE_ROOT"
echo "  source .venv/bin/activate"
echo ""
echo "To run samples:"
echo "  cd samples"
echo "  python sample_update_defaults.py"
echo ""
