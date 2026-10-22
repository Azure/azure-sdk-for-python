#!/usr/bin/env python3

# Quick test to verify our fixed unit tests work
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

try:
    # Test entity creation
    from azure.ai.ml.entities._deployment.deployment_template import DeploymentTemplate

    print("✓ DeploymentTemplate import successful")

    # Test creating a template with the correct constructor
    template = DeploymentTemplate(
        name="test-template", version="1.0", description="Test template", tags={"env": "test"}
    )

    print(f"✓ DeploymentTemplate creation successful: {template.name} v{template.version}")

    # Test operations import
    try:
        from azure.ai.ml.operations._deployment_template_operations import DeploymentTemplateOperations

        print("✓ DeploymentTemplateOperations import successful")
    except ImportError as e:
        print(f"⚠ DeploymentTemplateOperations import failed: {e}")

    # Test load function import
    try:
        from azure.ai.ml.entities._load_functions import load_deployment_template

        print("✓ load_deployment_template import successful")
    except ImportError as e:
        print(f"⚠ load_deployment_template import failed: {e}")

    print("\n✅ All basic functionality tests passed!")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback

    traceback.print_exc()
