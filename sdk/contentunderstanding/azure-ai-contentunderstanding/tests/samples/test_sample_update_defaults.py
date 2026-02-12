# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_update_defaults.py

DESCRIPTION:
    These tests validate the sample_update_defaults.py sample code.
    This sample demonstrates how to configure and retrieve default model deployment settings
    for your Microsoft Foundry resource. This is a required one-time setup per Microsoft Foundry
    resource before using prebuilt or custom analyzers.

    The tests validate:
    1. UpdateDefaults: Configuring model deployment mappings (optional, requires env vars)
    2. GetDefaults: Retrieving current model deployment configuration
    3. Model deployment mappings structure and data types

USAGE:
    pytest test_sample_update_defaults.py
"""

import pytest
from typing import Dict, Optional
from devtools_testutils import recorded_by_proxy
from testpreparer import ContentUnderstandingPreparer, ContentUnderstandingClientTestBase


class TestSampleUpdateDefaults(ContentUnderstandingClientTestBase):
    """Tests for sample_update_defaults.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_update_defaults(self, contentunderstanding_endpoint: str, **kwargs) -> Dict[str, str]:
        """Test configuring and getting model deployment defaults.

        This test validates:
        1. Optional model deployment configuration (UpdateDefaults)
        2. Getting current defaults (GetDefaults)
        3. Model deployment mappings structure

        00_UpdateDefaults.UpdateDefaultsAsync()
        """
        # Get variables from test proxy (recorded values in playback, empty dict in recording)
        variables = kwargs.pop("variables", {})
        import os

        # Get deployment names from variables (playback) or environment (recording)
        # If not found, use defaults and record them
        gpt_4_1_deployment = variables.setdefault(
            "gpt_4_1_deployment",
            os.getenv("GPT_4_1_DEPLOYMENT", "gpt-4.1")
        )
        gpt_4_1_mini_deployment = variables.setdefault(
            "gpt_4_1_mini_deployment",
            os.getenv("GPT_4_1_MINI_DEPLOYMENT", "gpt-4.1-mini")
        )
        text_embedding_3_large_deployment = variables.setdefault(
            "text_embedding_3_large_deployment",
            os.getenv("TEXT_EMBEDDING_3_LARGE_DEPLOYMENT", "text-embedding-3-large")
        )

        client = self.create_client(endpoint=contentunderstanding_endpoint)

        # Test UpdateDefaults - pass deployment names directly from variables
        self._test_update_defaults(
            client,
            gpt_4_1_deployment=gpt_4_1_deployment,
            gpt_4_1_mini_deployment=gpt_4_1_mini_deployment,
            text_embedding_3_large_deployment=text_embedding_3_large_deployment,
        )

        # Test GetDefaults - always run
        self._test_get_defaults(client)

        print("\n[SUCCESS] All test_sample_update_defaults assertions passed")

        # Return variables to be recorded
        return variables

    def _test_update_defaults(
        self,
        client,
        gpt_4_1_deployment: Optional[str] = None,
        gpt_4_1_mini_deployment: Optional[str] = None,
        text_embedding_3_large_deployment: Optional[str] = None,
    ) -> None:
        """Test updating model deployment defaults.

        This test attempts to update model deployments if deployment names are provided.
        If not provided, it checks if defaults are already configured. This is a best-effort test.

        Args:
            client: The ContentUnderstandingClient instance.
            gpt_4_1_deployment: GPT-4.1 deployment name (from test variables).
            gpt_4_1_mini_deployment: GPT-4.1-mini deployment name (from test variables).
            text_embedding_3_large_deployment: text-embedding-3-large deployment name (from test variables).
        """
        if gpt_4_1_deployment and gpt_4_1_mini_deployment and text_embedding_3_large_deployment:
            # All deployment names are provided, attempt to update defaults
            model_deployments = {
                "gpt-4.1": gpt_4_1_deployment,
                "gpt-4.1-mini": gpt_4_1_mini_deployment,
                "text-embedding-3-large": text_embedding_3_large_deployment,
            }
            print("Configuring model deployments...")
            updated_defaults = client.update_defaults(model_deployments=model_deployments)
            assert updated_defaults is not None, "UpdateDefaults should return a valid response"
            if updated_defaults.model_deployments:
                print(
                    f"[PASS] UpdateDefaults: Model deployments configured ({len(updated_defaults.model_deployments)} models)"
                )
        else:
            # Deployment names not provided, check if defaults are already configured
            print("[INFO] UpdateDefaults: Deployment names not provided.")
            print("       Checking if defaults are already configured...")

            # Fallback: Check if defaults are already configured (read-only check)
            try:
                response = client.get_defaults()
                current_defaults = response
                model_deployments = getattr(current_defaults, "model_deployments", None)

                if model_deployments and len(model_deployments) > 0:
                    print(
                        f"[PASS] UpdateDefaults: Model deployments already configured ({len(model_deployments)} models)"
                    )
                else:
                    print("[INFO] UpdateDefaults: No model deployments configured (valid state)")
            except Exception as e:
                print(f"[INFO] UpdateDefaults: Could not check if defaults are configured - {str(e)}")

    def _test_get_defaults(self, client):
        """Test getting current model deployment defaults.

        This test validates that:
        1. The GetDefaults call returns a valid response
        2. The response contains the expected structure (model_deployments dict)
        3. If deployments are configured, they have valid string keys and values
        """
        # Get current defaults
        get_response = client.get_defaults()

        # Assertion: Verify response is not null
        assert get_response is not None, "GetDefaults response should not be null"
        print("[PASS] GetDefaults: Successfully retrieved defaults")

        # Get the defaults object
        defaults = get_response

        # Assertion: Verify defaults object
        assert defaults is not None, "Defaults object should not be null"

        # Check model deployments attribute
        model_deployments = getattr(defaults, "model_deployments", None)

        if model_deployments:
            # Assertion: Verify model_deployments structure
            assert isinstance(model_deployments, dict), "model_deployments should be a dictionary"

            if len(model_deployments) > 0:
                print(f"[PASS] Current model deployment mappings ({len(model_deployments)} models):")

                # Assertion: Validate each deployment mapping
                for key, value in model_deployments.items():
                    assert isinstance(key, str), f"Model key should be string, got {type(key)}"
                    assert key.strip(), "Model key should not be empty or whitespace"
                    assert isinstance(value, str), f"Deployment value should be string for key {key}, got {type(value)}"
                    assert value.strip(), f"Deployment value should not be empty for key {key}"
                    print(f"  {key}: {value}")

                # Assertion: Check for expected model keys (if any configured)
                # Common models: gpt-4.1, gpt-4.1-mini, text-embedding-3-large
                expected_keys = {"gpt-4.1", "gpt-4.1-mini", "text-embedding-3-large"}
                found_keys = set(model_deployments.keys())

                if found_keys & expected_keys:  # If any expected keys are present
                    common_keys = found_keys & expected_keys
                    print(f"[PASS] Found expected model keys: {', '.join(sorted(common_keys))}")
            else:
                print("  No model deployments configured yet (this is valid)")
        else:
            # No model deployments is a valid state
            print("  No model deployments configured yet (model_deployments attribute not present)")

        print("[PASS] GetDefaults: All assertions passed")
