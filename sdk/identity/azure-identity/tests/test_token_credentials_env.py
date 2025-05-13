# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from unittest.mock import patch

import pytest

from azure.identity import (
    AzureCliCredential,
    AzureDeveloperCliCredential,
    AzurePowerShellCredential,
    DefaultAzureCredential,
    EnvironmentCredential,
    ManagedIdentityCredential,
    SharedTokenCacheCredential,
    WorkloadIdentityCredential,
)
from azure.identity._constants import EnvironmentVariables


def test_token_credentials_env_dev():
    """With AZURE_TOKEN_CREDENTIALS=dev, DefaultAzureCredential should use only developer credentials"""

    prod_credentials = {EnvironmentCredential, WorkloadIdentityCredential, ManagedIdentityCredential}

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "dev"}, clear=False):
        credential = DefaultAzureCredential()

        # Get the actual credential classes in the chain
        actual_classes = {c.__class__ for c in credential.credentials}

        # All dev credentials should be present (if supported)
        if SharedTokenCacheCredential.supported():
            assert SharedTokenCacheCredential in actual_classes

        # Other developer credentials should be present
        assert AzureCliCredential in actual_classes
        assert AzureDeveloperCliCredential in actual_classes
        assert AzurePowerShellCredential in actual_classes

        # Production credentials should NOT be present
        for cred_class in prod_credentials:
            if cred_class == WorkloadIdentityCredential:
                # Skip this check unless env vars are set
                if not all(os.environ.get(var) for var in EnvironmentVariables.WORKLOAD_IDENTITY_VARS):
                    continue
            assert cred_class not in actual_classes


def test_token_credentials_env_prod():
    """With AZURE_TOKEN_CREDENTIALS=prod, DefaultAzureCredential should use only production credentials"""

    dev_credentials = {
        SharedTokenCacheCredential,
        AzureCliCredential,
        AzureDeveloperCliCredential,
        AzurePowerShellCredential,
    }

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "prod"}, clear=False):
        # Print to verify the environment variable is set in the test
        print(f"AZURE_TOKEN_CREDENTIALS={os.environ.get(EnvironmentVariables.AZURE_TOKEN_CREDENTIALS)}")

        credential = DefaultAzureCredential()

        # Get the actual credential classes in the chain
        actual_classes = {c.__class__ for c in credential.credentials}

        # Print which credentials are actually in the chain
        print("Credentials in chain:")
        for cls in actual_classes:
            print(f" - {cls.__name__}")

        # Production credentials should be present
        assert EnvironmentCredential in actual_classes
        assert ManagedIdentityCredential in actual_classes

        # Check WorkloadIdentityCredential only if env vars are set
        if all(os.environ.get(var) for var in EnvironmentVariables.WORKLOAD_IDENTITY_VARS):
            assert WorkloadIdentityCredential in actual_classes

        # Developer credentials should NOT be present
        for cred_class in dev_credentials:
            assert cred_class not in actual_classes


def test_token_credentials_env_case_insensitive():
    """AZURE_TOKEN_CREDENTIALS should be case insensitive"""

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "DeV"}, clear=False):
        credential = DefaultAzureCredential()

        # Get the actual credential classes in the chain
        actual_classes = {c.__class__ for c in credential.credentials}

        # EnvironmentCredential (prod) should not be present
        assert EnvironmentCredential not in actual_classes

        # AzureCliCredential (dev) should be present
        assert AzureCliCredential in actual_classes


def test_token_credentials_env_invalid():
    """Invalid AZURE_TOKEN_CREDENTIALS value should raise an error"""

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "invalid"}, clear=False):
        with pytest.raises(ValueError):
            credential = DefaultAzureCredential()


def test_token_credentials_env_with_exclude():
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "prod"}, clear=False):
        credential = DefaultAzureCredential(exclude_environment_credential=True)
        actual_classes = {c.__class__ for c in credential.credentials}

        assert EnvironmentCredential not in actual_classes
