# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from unittest.mock import Mock, patch

import pytest

from azure.ai.ml._artifacts._artifact_utilities import get_datastore_info
from azure.ai.ml._restclient.v2022_10_01.models import DatastoreType
from azure.ai.ml.entities._credentials import (
    AccountKeyConfiguration,
    NoneCredentialConfiguration,
    SasTokenConfiguration,
)
from azure.ai.ml.entities._datastore.azure_storage import AzureBlobDatastore


@pytest.mark.unittest
class TestArtifactUtilities:
    """Tests for artifact utilities functions."""

    def test_get_datastore_info_with_identity_based_credentials(self):
        """Test that get_datastore_info doesn't call _list_secrets for identity-based datastores."""
        # Create a mock datastore with NoneCredentialConfiguration (identity-based)
        mock_datastore = Mock(spec=AzureBlobDatastore)
        mock_datastore.type = DatastoreType.AZURE_BLOB
        mock_datastore.account_name = "testaccount"
        mock_datastore.container_name = "testcontainer"
        mock_datastore.credentials = NoneCredentialConfiguration()

        # Create a mock DatastoreOperations
        mock_operations = Mock()
        mock_operations.get.return_value = mock_datastore
        mock_operations._credential = Mock()

        # Call get_datastore_info
        with patch("azure.ai.ml._artifacts._artifact_utilities._get_storage_endpoint_from_metadata") as mock_endpoint:
            mock_endpoint.return_value = "core.windows.net"
            result = get_datastore_info(mock_operations, "test-datastore")

        # Verify that _list_secrets was NOT called for identity-based datastore
        mock_operations._list_secrets.assert_not_called()

        # Verify that the credential from operations was used
        assert result["credential"] == mock_operations._credential
        assert result["storage_type"] == DatastoreType.AZURE_BLOB
        assert result["storage_account"] == "testaccount"
        assert result["container_name"] == "testcontainer"

    def test_get_datastore_info_with_sas_token_credentials(self):
        """Test that get_datastore_info calls _list_secrets for SAS token datastores."""
        # Create a mock datastore with SasTokenConfiguration
        mock_datastore = Mock(spec=AzureBlobDatastore)
        mock_datastore.type = DatastoreType.AZURE_BLOB
        mock_datastore.account_name = "testaccount"
        mock_datastore.container_name = "testcontainer"
        mock_datastore.credentials = SasTokenConfiguration(sas_token="test-sas-token")

        # Create a mock DatastoreOperations
        mock_operations = Mock()
        mock_operations.get.return_value = mock_datastore
        mock_operations._credential = Mock()
        
        # Mock _list_secrets to return a SAS token
        mock_secrets = Mock()
        mock_secrets.sas_token = "generated-sas-token"
        mock_operations._list_secrets.return_value = mock_secrets

        # Call get_datastore_info
        with patch("azure.ai.ml._artifacts._artifact_utilities._get_storage_endpoint_from_metadata") as mock_endpoint:
            mock_endpoint.return_value = "core.windows.net"
            result = get_datastore_info(mock_operations, "test-datastore")

        # Verify that _list_secrets WAS called for SAS token datastore
        mock_operations._list_secrets.assert_called_once_with(name="test-datastore", expirable_secret=True)

        # Verify that the SAS token from _list_secrets was used
        assert result["credential"] == "generated-sas-token"
        assert result["storage_type"] == DatastoreType.AZURE_BLOB
        assert result["storage_account"] == "testaccount"
        assert result["container_name"] == "testcontainer"

    def test_get_datastore_info_with_account_key_credentials(self):
        """Test that get_datastore_info calls _list_secrets for account key datastores."""
        # Create a mock datastore with AccountKeyConfiguration
        mock_datastore = Mock(spec=AzureBlobDatastore)
        mock_datastore.type = DatastoreType.AZURE_BLOB
        mock_datastore.account_name = "testaccount"
        mock_datastore.container_name = "testcontainer"
        mock_datastore.credentials = AccountKeyConfiguration(account_key="test-key")

        # Create a mock DatastoreOperations
        mock_operations = Mock()
        mock_operations.get.return_value = mock_datastore
        mock_operations._credential = Mock()
        
        # Mock _list_secrets to return a SAS token
        mock_secrets = Mock()
        mock_secrets.sas_token = "generated-sas-token-from-key"
        mock_operations._list_secrets.return_value = mock_secrets

        # Call get_datastore_info
        with patch("azure.ai.ml._artifacts._artifact_utilities._get_storage_endpoint_from_metadata") as mock_endpoint:
            mock_endpoint.return_value = "core.windows.net"
            result = get_datastore_info(mock_operations, "test-datastore")

        # Verify that _list_secrets WAS called for account key datastore
        mock_operations._list_secrets.assert_called_once_with(name="test-datastore", expirable_secret=True)

        # Verify that the SAS token from _list_secrets was used
        assert result["credential"] == "generated-sas-token-from-key"
        assert result["storage_type"] == DatastoreType.AZURE_BLOB
        assert result["storage_account"] == "testaccount"
        assert result["container_name"] == "testcontainer"
