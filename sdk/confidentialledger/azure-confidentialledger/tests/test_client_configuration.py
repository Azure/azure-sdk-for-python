# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for ConfidentialLedgerClient configuration."""

import os
import tempfile

import pytest
from unittest.mock import patch, MagicMock
from azure.core.pipeline import policies

from azure.confidentialledger._redirect_caching_policy import RedirectCachingPolicy


class TestClientConfiguration:
    """Tests for client configuration settings."""

    def test_sensitive_header_cleanup_policy_disable_redirect_cleanup_enabled(self):
        """Test that SensitiveHeaderCleanupPolicy has disable_redirect_cleanup=True.

        This ensures that authentication and ledger-specific headers are preserved
        on service-managed redirects, which is required for correct authentication
        behavior within the trusted Confidential Ledger endpoint.
        """
        with (
            patch("azure.confidentialledger._client.PipelineClient") as mock_pipeline_client,
            patch(
                "azure.confidentialledger._patch.ConfidentialLedgerCertificateClient"
            ) as mock_cert_client,
        ):
            mock_pipeline_client.return_value = MagicMock()
            mock_cert_client.return_value.get_ledger_identity.return_value = {
                "ledgerTlsCertificate": "fake-cert"
            }

            with tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False) as f:
                f.write("fake-cert")
                cert_path = f.name

            try:
                from azure.confidentialledger._patch import (
                    ConfidentialLedgerClient,
                    ConfidentialLedgerCertificateCredential,
                )

                cred = ConfidentialLedgerCertificateCredential(cert_path)
                client = ConfidentialLedgerClient(
                    "https://test-ledger.confidentialledger.azure.com",
                    cred,
                    ledger_certificate_path=cert_path,
                )

                call_args = mock_pipeline_client.call_args
                policies_arg = call_args.kwargs.get("policies") or call_args[1].get("policies")

                sensitive_header_policy = None
                for policy in policies_arg:
                    if isinstance(policy, policies.SensitiveHeaderCleanupPolicy):
                        sensitive_header_policy = policy
                        break

                assert (
                    sensitive_header_policy is not None
                ), "SensitiveHeaderCleanupPolicy should be present in the client's policies"
                assert sensitive_header_policy._disable_redirect_cleanup is True, (
                    "SensitiveHeaderCleanupPolicy should have disable_redirect_cleanup=True "
                    "to preserve authentication headers on Confidential Ledger redirects"
                )

                client.close()
            finally:
                os.unlink(cert_path)

    def test_redirect_caching_policy_is_used(self):
        """Test that RedirectCachingPolicy is used as the redirect policy."""
        with (
            patch("azure.confidentialledger._client.PipelineClient") as mock_pipeline_client,
            patch(
                "azure.confidentialledger._patch.ConfidentialLedgerCertificateClient"
            ) as mock_cert_client,
        ):
            mock_pipeline_client.return_value = MagicMock()
            mock_cert_client.return_value.get_ledger_identity.return_value = {
                "ledgerTlsCertificate": "fake-cert"
            }

            with tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False) as f:
                f.write("fake-cert")
                cert_path = f.name

            try:
                from azure.confidentialledger._patch import (
                    ConfidentialLedgerClient,
                    ConfidentialLedgerCertificateCredential,
                )

                cred = ConfidentialLedgerCertificateCredential(cert_path)
                client = ConfidentialLedgerClient(
                    "https://test-ledger.confidentialledger.azure.com",
                    cred,
                    ledger_certificate_path=cert_path,
                )

                call_args = mock_pipeline_client.call_args
                policies_arg = call_args.kwargs.get("policies") or call_args[1].get("policies")

                redirect_policy = None
                for policy in policies_arg:
                    if isinstance(policy, RedirectCachingPolicy):
                        redirect_policy = policy
                        break

                assert redirect_policy is not None, (
                    "RedirectCachingPolicy should be used as the redirect policy"
                )

                client.close()
            finally:
                os.unlink(cert_path)
