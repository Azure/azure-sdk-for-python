# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for ConfidentialLedgerClient configuration."""

import pytest
from unittest.mock import patch, MagicMock
from azure.core.pipeline import policies

# Import the generated client directly to test its policy configuration
from azure.confidentialledger._client import ConfidentialLedgerClient as GeneratedClient


class TestClientConfiguration:
    """Tests for client configuration settings."""

    def test_sensitive_header_cleanup_policy_disable_redirect_cleanup_enabled(self):
        """Test that SensitiveHeaderCleanupPolicy has disable_redirect_cleanup=True.

        This ensures that authentication and ledger-specific headers are preserved
        on service-managed redirects, which is required for correct authentication
        behavior within the trusted Confidential Ledger endpoint.
        """
        # Mock the PipelineClient to capture the policies passed to it
        with patch("azure.confidentialledger._client.PipelineClient") as mock_pipeline_client:
            mock_pipeline_client.return_value = MagicMock()

            # Create the generated client directly - this will trigger policy creation
            # The generated client only requires ledger_endpoint
            client = GeneratedClient(
                ledger_endpoint="https://test-ledger.confidentialledger.azure.com"
            )

            # Get the policies argument passed to PipelineClient
            call_args = mock_pipeline_client.call_args
            policies_arg = call_args.kwargs.get("policies") or call_args[1].get("policies")

            # Find the SensitiveHeaderCleanupPolicy in the policies list
            sensitive_header_policy = None
            for policy in policies_arg:
                if isinstance(policy, policies.SensitiveHeaderCleanupPolicy):
                    sensitive_header_policy = policy
                    break

            # Assert the policy exists and has disable_redirect_cleanup=True
            assert sensitive_header_policy is not None, (
                "SensitiveHeaderCleanupPolicy should be present in the client's policies"
            )
            assert sensitive_header_policy._disable_redirect_cleanup is True, (
                "SensitiveHeaderCleanupPolicy should have disable_redirect_cleanup=True "
                "to preserve authentication headers on Confidential Ledger redirects"
            )

            client.close()

    def test_sensitive_header_cleanup_policy_is_in_correct_position(self):
        """Test that SensitiveHeaderCleanupPolicy is positioned after authentication_policy.

        The policy should be placed after the authentication policy so that it can
        properly handle the redirect cleanup for authentication headers.
        """
        with patch("azure.confidentialledger._client.PipelineClient") as mock_pipeline_client:
            mock_pipeline_client.return_value = MagicMock()

            client = GeneratedClient(
                ledger_endpoint="https://test-ledger.confidentialledger.azure.com"
            )

            # Get the policies argument passed to PipelineClient
            call_args = mock_pipeline_client.call_args
            policies_arg = call_args.kwargs.get("policies") or call_args[1].get("policies")

            # Filter out None values
            non_none_policies = [p for p in policies_arg if p is not None]

            # Find positions of key policies
            sensitive_header_idx = None
            distributed_tracing_idx = None

            for idx, policy in enumerate(non_none_policies):
                if isinstance(policy, policies.SensitiveHeaderCleanupPolicy):
                    sensitive_header_idx = idx
                elif isinstance(policy, policies.DistributedTracingPolicy):
                    distributed_tracing_idx = idx

            # SensitiveHeaderCleanupPolicy should come after DistributedTracingPolicy
            assert sensitive_header_idx is not None, (
                "SensitiveHeaderCleanupPolicy should be present in the policies"
            )
            assert distributed_tracing_idx is not None, (
                "DistributedTracingPolicy should be present in the policies"
            )
            assert sensitive_header_idx > distributed_tracing_idx, (
                "SensitiveHeaderCleanupPolicy should be positioned after DistributedTracingPolicy"
            )

            client.close()
