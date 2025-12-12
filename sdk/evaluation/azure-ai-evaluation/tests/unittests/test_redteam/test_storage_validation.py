# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for storage account validation functionality."""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch
from azure.ai.evaluation._common.evaluation_onedp_client import EvaluationServiceOneDPClient
from azure.ai.evaluation._common.utils import upload
from azure.ai.evaluation._exceptions import EvaluationException
from azure.ai.evaluation.red_team._mlflow_integration import MLflowIntegration


class TestStorageValidation(unittest.TestCase):
    """Test cases for storage account validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_credential = Mock()
        self.test_endpoint = "https://test-endpoint.azure.com"

    @patch("azure.ai.evaluation._common.evaluation_onedp_client.RestEvaluationServiceClient")
    def test_test_storage_upload_success(self, mock_rest_client_class):
        """Test successful storage upload validation."""
        # Arrange
        mock_rest_client = Mock()
        mock_rest_client_class.return_value = mock_rest_client

        mock_pending_upload_response = Mock()
        mock_pending_upload_response.blob_reference_for_consumption = Mock()
        mock_pending_upload_response.blob_reference_for_consumption.credential = Mock()
        mock_pending_upload_response.blob_reference_for_consumption.credential.sas_uri = (
            "https://test.blob.core.windows.net/container?sas_token"
        )

        mock_rest_client.evaluation_results.start_pending_upload.return_value = mock_pending_upload_response

        # Mock ContainerClient
        with patch(
            "azure.ai.evaluation._common.evaluation_onedp_client.ContainerClient"
        ) as mock_container_client_class:
            mock_container_client = Mock()
            mock_container_client.__enter__ = Mock(return_value=mock_container_client)
            mock_container_client.__exit__ = Mock(return_value=None)
            mock_container_client_class.from_container_url.return_value = mock_container_client

            # Mock the upload_blob method to succeed
            mock_container_client.upload_blob = Mock()
            # Act
            client = EvaluationServiceOneDPClient(self.test_endpoint, self.mock_credential)
            result = client.test_storage_upload()

            # Assert
            self.assertTrue(result)
            mock_container_client.upload_blob.assert_called_once()

    @patch("azure.ai.evaluation._common.evaluation_onedp_client.RestEvaluationServiceClient")
    def test_test_storage_upload_failure(self, mock_rest_client_class):
        """Test storage upload validation failure."""
        # Arrange
        mock_rest_client = Mock()
        mock_rest_client_class.return_value = mock_rest_client

        # Simulate upload failure
        mock_rest_client.evaluation_results.start_pending_upload.side_effect = Exception(
            "Storage account not accessible"
        )

        # Act & Assert
        client = EvaluationServiceOneDPClient(self.test_endpoint, self.mock_credential)
        with self.assertRaises(EvaluationException) as context:
            client.test_storage_upload()

        # Verify error message contains helpful guidance
        self.assertIn("storage", str(context.exception).lower())
        self.assertIn("permissions", str(context.exception).lower())

    def test_mlflow_integration_test_storage_upload_onedp(self):
        """Test MLflowIntegration storage validation for OneDP projects."""
        # Arrange
        mock_logger = Mock()
        mock_generated_rai_client = Mock()
        mock_evaluation_client = Mock()
        mock_evaluation_client.test_storage_upload.return_value = True
        mock_generated_rai_client._evaluation_onedp_client = mock_evaluation_client

        mlflow_integration = MLflowIntegration(
            logger=mock_logger, generated_rai_client=mock_generated_rai_client, one_dp_project=True
        )

        # Act
        result = mlflow_integration.test_storage_upload()

        # Assert
        self.assertTrue(result)
        mock_evaluation_client.test_storage_upload.assert_called_once()

    def test_mlflow_integration_test_storage_upload_non_onedp(self):
        """Test MLflowIntegration storage validation for non-OneDP projects."""
        # Arrange
        mock_logger = Mock()
        mock_generated_rai_client = Mock()

        mlflow_integration = MLflowIntegration(
            logger=mock_logger, generated_rai_client=mock_generated_rai_client, one_dp_project=False
        )

        # Act
        result = mlflow_integration.test_storage_upload()

        # Assert
        # For non-OneDP projects, we skip the test and return True
        self.assertTrue(result)


class TestUploadErrorMessages(unittest.TestCase):
    """Test cases for improved upload error messages."""

    @patch("azure.ai.evaluation._common.utils.ContainerClient")
    def test_upload_error_message_includes_guidance(self, mock_container_client_class):
        """Test that upload errors include helpful troubleshooting guidance."""
        # Arrange
        mock_container_client = Mock()
        mock_container_client.account_name = "testaccount"
        mock_container_client.upload_blob.side_effect = Exception("Connection refused")

        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp_file:
            tmp_file.write("test content")
            test_file_path = tmp_file.name

        # Act & Assert
        try:
            with self.assertRaises(EvaluationException) as context:
                upload(path=test_file_path, container_client=mock_container_client)

            # Verify error message contains helpful guidance
            error_message = str(context.exception)
            self.assertIn("storage account", error_message.lower())
            self.assertIn("permissions", error_message.lower())
            self.assertIn("verify", error_message.lower())
        finally:
            # Clean up the temporary file
            try:
                os.unlink(test_file_path)
            except Exception:
                pass


if __name__ == "__main__":
    unittest.main()
