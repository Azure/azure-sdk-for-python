# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_update_defaults_async.py

DESCRIPTION:
    These tests validate the sample_update_defaults_async.py sample code.
    This sample demonstrates how to configure and retrieve default model deployment settings
    for your Microsoft Foundry resource. This is a required one-time setup per Microsoft Foundry
    resource before using prebuilt or custom analyzers.

    The tests validate:
    1. UpdateDefaults: Configuring model deployment mappings (optional, requires env vars)
    2. GetDefaults: Retrieving current model deployment configuration (async)
    3. Model deployment mappings structure and data types

USAGE:
    pytest test_sample_update_defaults_async.py
"""

import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer_async import ContentUnderstandingPreparer, ContentUnderstandingClientTestBaseAsync


class TestSampleUpdateDefaultsAsync(ContentUnderstandingClientTestBaseAsync):
    """Tests for sample_update_defaults.py (async version)"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_update_defaults_async(self, contentunderstanding_endpoint: str) -> None:
        """Test configuring and getting model deployment defaults (async version).

        This test validates:
        1. Optional model deployment configuration (UpdateDefaults)
        2. Getting current defaults (GetDefaults)
        3. Model deployment mappings structure

        00_UpdateDefaults.UpdateDefaultsAsync()
        """
        client = self.create_async_client(endpoint=contentunderstanding_endpoint)

        # Test UpdateDefaults - only if deployment names are provided
        await self._test_update_defaults(client)

        # Test GetDefaults - always run
        await self._test_get_defaults(client)

        await client.close()
        print("\n[SUCCESS] All test_sample_update_defaults_async assertions passed")

    async def _test_update_defaults(self, client):
        """Test updating model deployment defaults (async).

        This test attempts to update model deployments if deployment names are provided
        via environment variables. If not provided, it checks if defaults are already
        configured. This is a best-effort test.
        """
        import os

        gpt_4_1_deployment = os.getenv("GPT_4_1_DEPLOYMENT")
        gpt_4_1_mini_deployment = os.getenv("GPT_4_1_MINI_DEPLOYMENT")
        text_embedding_3_large_deployment = os.getenv("TEXT_EMBEDDING_3_LARGE_DEPLOYMENT")

        if gpt_4_1_deployment and gpt_4_1_mini_deployment and text_embedding_3_large_deployment:
            # All deployment names are provided, attempt to update defaults
            model_deployments = {
                "gpt-4.1": gpt_4_1_deployment,
                "gpt-4.1-mini": gpt_4_1_mini_deployment,
                "text-embedding-3-large": text_embedding_3_large_deployment,
            }
            print("Configuring model deployments...")
            updated_defaults = await client.update_defaults(model_deployments=model_deployments)
            assert updated_defaults is not None, "UpdateDefaults should return a valid response"
            if updated_defaults.model_deployments:
                print(
                    f"[PASS] UpdateDefaults: Model deployments configured ({len(updated_defaults.model_deployments)} models)"
                )
        else:
            # Deployment names not provided, check if defaults are already configured
            print("[INFO] UpdateDefaults: Deployment names not set in environment variables.")
            print("       Checking if defaults are already configured...")

            # Fallback: Check if defaults are already configured (read-only check)
            try:
                response = await client.get_defaults()
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

    async def _test_get_defaults(self, client):
        """Test getting current model deployment defaults (async).

        This test validates that:
        1. The GetDefaults call returns a valid response (async)
        2. The response contains the expected structure (model_deployments dict)
        3. If deployments are configured, they have valid string keys and values
        """
        # Get current defaults
        get_response = await client.get_defaults()

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
