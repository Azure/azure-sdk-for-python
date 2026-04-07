# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import re
import tempfile
import pytest
from unittest.mock import MagicMock, patch, call
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.ai.projects.operations._patch_evaluators import BetaEvaluatorsOperations, _EVALUATORS_FOUNDRY_FEATURES_VALUE
from azure.ai.projects.models import CodeBasedEvaluatorDefinition, EvaluatorVersion
from azure.ai.projects.models._patch import _FOUNDRY_FEATURES_HEADER_NAME

_EVALUATORS_HEADERS = {_FOUNDRY_FEATURES_HEADER_NAME: _EVALUATORS_FOUNDRY_FEATURES_VALUE}


class TestEvaluatorsUpload:
    """Unit tests for BetaEvaluatorsOperations.upload() method."""

    def _create_operations(self):
        """Create a mock BetaEvaluatorsOperations instance with mocked service calls."""
        ops = object.__new__(BetaEvaluatorsOperations)
        ops.start_pending_upload = MagicMock()
        ops.list_versions = MagicMock()
        ops.create_version = MagicMock()
        return ops

    def _create_temp_folder(self, files=None):
        """Create a temporary folder with files for testing.

        :param files: dict of {relative_path: content_bytes}
        :return: path to temp folder
        """
        tmp_dir = tempfile.mkdtemp()
        if files is None:
            files = {"evaluator.py": b"class MyEvaluator:\n    pass\n"}
        for rel_path, content in files.items():
            full_path = os.path.join(tmp_dir, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "wb") as f:
                f.write(content)
        return tmp_dir

    def _mock_pending_upload_response(self, blob_uri="https://storage.blob.core.windows.net/container-1"):
        """Return a mock pending upload response dict."""
        return {
            "blobReferenceForConsumption": {
                "blobUri": blob_uri,
                "credential": {
                    "sasUri": f"{blob_uri}?sv=2025-01-05&sig=fakesig",
                },
            }
        }

    # ---------------------------------------------------------------
    # upload() - input validation tests
    # ---------------------------------------------------------------

    def test_upload_raises_if_folder_does_not_exist(self):
        ops = self._create_operations()
        ops.list_versions.side_effect = ResourceNotFoundError("Not found")

        with pytest.raises(ValueError, match="does not exist"):
            ops.upload(
                name="test_evaluator",
                evaluator_version={"definition": {}},
                folder="/nonexistent/path/abc123",
            )

    def test_upload_raises_if_path_is_file(self):
        ops = self._create_operations()
        ops.list_versions.side_effect = ResourceNotFoundError("Not found")

        with tempfile.NamedTemporaryFile(suffix=".py") as tmp:
            with pytest.raises(ValueError, match="file, not a folder"):
                ops.upload(
                    name="test_evaluator",
                    evaluator_version={"definition": {}},
                    folder=tmp.name,
                )

    def test_upload_raises_if_folder_is_empty(self):
        ops = self._create_operations()
        ops.list_versions.side_effect = ResourceNotFoundError("Not found")
        ops.start_pending_upload.return_value = self._mock_pending_upload_response()

        empty_dir = tempfile.mkdtemp()

        with patch("azure.ai.projects.operations._patch_evaluators.ContainerClient") as MockContainerClient:
            mock_container = MagicMock()
            MockContainerClient.from_container_url.return_value = mock_container
            mock_container.__enter__ = MagicMock(return_value=mock_container)
            mock_container.__exit__ = MagicMock(return_value=False)

            with pytest.raises(ValueError, match="folder is empty"):
                ops.upload(
                    name="test_evaluator",
                    evaluator_version={"definition": {}},
                    folder=empty_dir,
                )

    # ---------------------------------------------------------------
    # upload() - version auto-increment tests
    # ---------------------------------------------------------------

    def test_get_next_version_returns_1_for_new_evaluator(self):
        ops = self._create_operations()
        ops.list_versions.side_effect = ResourceNotFoundError("Not found")
        assert ops._get_next_version("new_evaluator") == "1"

    def test_get_next_version_returns_1_for_empty_list(self):
        ops = self._create_operations()
        ops.list_versions.return_value = []
        assert ops._get_next_version("empty_evaluator") == "1"

    def test_get_next_version_increments_highest_version(self):
        ops = self._create_operations()
        ops.list_versions.return_value = [
            {"version": "1"},
            {"version": "3"},
            {"version": "2"},
        ]
        assert ops._get_next_version("existing_evaluator") == "4"

    def test_get_next_version_ignores_non_numeric_versions(self):
        ops = self._create_operations()
        ops.list_versions.return_value = [
            {"version": "1"},
            {"version": "latest"},
            {"version": "beta"},
        ]
        assert ops._get_next_version("mixed_evaluator") == "2"

    # ---------------------------------------------------------------
    # upload() - pending upload / SAS URI validation tests
    # ---------------------------------------------------------------

    def test_start_pending_upload_raises_if_no_blob_ref(self):
        ops = self._create_operations()
        ops.start_pending_upload.return_value = {}

        with pytest.raises(ValueError, match="Blob reference is not present"):
            ops._start_pending_upload_and_get_container_client("test", "1")

    def test_start_pending_upload_raises_if_no_credential(self):
        ops = self._create_operations()
        ops.start_pending_upload.return_value = {
            "blobReferenceForConsumption": {
                "blobUri": "https://storage.blob.core.windows.net/container",
            }
        }

        with pytest.raises(ValueError, match="SAS credential is not present"):
            ops._start_pending_upload_and_get_container_client("test", "1")

    def test_start_pending_upload_raises_if_no_sas_uri(self):
        ops = self._create_operations()
        ops.start_pending_upload.return_value = {
            "blobReferenceForConsumption": {
                "blobUri": "https://storage.blob.core.windows.net/container",
                "credential": {"type": "SAS"},
            }
        }

        with pytest.raises(ValueError, match="SAS URI is missing"):
            ops._start_pending_upload_and_get_container_client("test", "1")

    def test_start_pending_upload_raises_if_no_blob_uri(self):
        ops = self._create_operations()
        ops.start_pending_upload.return_value = {
            "blobReferenceForConsumption": {
                "credential": {
                    "sasUri": "https://storage.blob.core.windows.net/container?sig=fake",
                },
            }
        }

        with pytest.raises(ValueError, match="Blob URI is missing"):
            ops._start_pending_upload_and_get_container_client("test", "1")

    def test_start_pending_upload_passes_connection_name(self):
        ops = self._create_operations()
        ops.start_pending_upload.return_value = self._mock_pending_upload_response()

        with patch("azure.ai.projects.operations._patch_evaluators.ContainerClient"):
            ops._start_pending_upload_and_get_container_client("test", "1", connection_name="my-connection")

        ops.start_pending_upload.assert_called_once_with(
            name="test",
            version="1",
            pending_upload_request={"connectionName": "my-connection"},
            headers=_EVALUATORS_HEADERS,
        )

    # ---------------------------------------------------------------
    # upload() - file upload behavior tests
    # ---------------------------------------------------------------

    def test_upload_uploads_single_file(self):
        ops = self._create_operations()
        ops.list_versions.side_effect = ResourceNotFoundError("Not found")
        ops.start_pending_upload.return_value = self._mock_pending_upload_response()
        ops.create_version.return_value = {"name": "test", "version": "1"}

        folder = self._create_temp_folder({"evaluator.py": b"class Eval: pass"})

        with patch("azure.ai.projects.operations._patch_evaluators.ContainerClient") as MockContainerClient:
            mock_container = MagicMock()
            MockContainerClient.from_container_url.return_value = mock_container
            mock_container.__enter__ = MagicMock(return_value=mock_container)
            mock_container.__exit__ = MagicMock(return_value=False)

            ops.upload(
                name="test",
                evaluator_version={"definition": {}},
                folder=folder,
            )

            mock_container.upload_blob.assert_called_once()
            blob_name = mock_container.upload_blob.call_args.kwargs.get("name") or mock_container.upload_blob.call_args[
                1
            ].get("name")
            assert blob_name == "evaluator.py"

    def test_upload_handles_nested_folders(self):
        ops = self._create_operations()
        ops.list_versions.side_effect = ResourceNotFoundError("Not found")
        ops.start_pending_upload.return_value = self._mock_pending_upload_response()
        ops.create_version.return_value = {"name": "test", "version": "1"}

        folder = self._create_temp_folder(
            {
                "evaluator.py": b"class Eval: pass",
                "utils/__init__.py": b"",
                "utils/helper.py": b"def helper(): pass",
            }
        )

        with patch("azure.ai.projects.operations._patch_evaluators.ContainerClient") as MockContainerClient:
            mock_container = MagicMock()
            MockContainerClient.from_container_url.return_value = mock_container
            mock_container.__enter__ = MagicMock(return_value=mock_container)
            mock_container.__exit__ = MagicMock(return_value=False)

            ops.upload(
                name="test",
                evaluator_version={"definition": {}},
                folder=folder,
            )

            assert mock_container.upload_blob.call_count == 3
            uploaded_names = sorted(
                c.kwargs.get("name") or c[1].get("name") for c in mock_container.upload_blob.call_args_list
            )
            assert uploaded_names == sorted(["evaluator.py", "utils/__init__.py", "utils/helper.py"])

    def test_upload_skips_pycache_and_pyc_files_with_patterns(self):
        ops = self._create_operations()
        ops.list_versions.side_effect = ResourceNotFoundError("Not found")
        ops.start_pending_upload.return_value = self._mock_pending_upload_response()
        ops.create_version.return_value = {"name": "test", "version": "1"}

        folder = self._create_temp_folder(
            {
                "evaluator.py": b"class Eval: pass",
                "__pycache__/evaluator.cpython-312.pyc": b"compiled",
                "other.pyc": b"compiled",
                "other.pyo": b"optimized",
            }
        )

        file_pattern = re.compile(r"^(?!\.).+(?<!\.pyc)(?<!\.pyo)$")
        folder_exclusions_pattern = re.compile(r"^(\..*|__pycache__|venv|node_modules)$")

        with patch("azure.ai.projects.operations._patch_evaluators.ContainerClient") as MockContainerClient:
            mock_container = MagicMock()
            MockContainerClient.from_container_url.return_value = mock_container
            mock_container.__enter__ = MagicMock(return_value=mock_container)
            mock_container.__exit__ = MagicMock(return_value=False)

            ops.upload(
                name="test",
                evaluator_version={"definition": {}},
                folder=folder,
                file_pattern=file_pattern,
                folder_exclusions_pattern=folder_exclusions_pattern,
            )

            # Only evaluator.py should be uploaded
            assert mock_container.upload_blob.call_count == 1
            blob_name = mock_container.upload_blob.call_args.kwargs.get("name") or mock_container.upload_blob.call_args[
                1
            ].get("name")
            assert blob_name == "evaluator.py"

    def test_upload_uploads_all_files_without_patterns(self):
        ops = self._create_operations()
        ops.list_versions.side_effect = ResourceNotFoundError("Not found")
        ops.start_pending_upload.return_value = self._mock_pending_upload_response()
        ops.create_version.return_value = {"name": "test", "version": "1"}

        folder = self._create_temp_folder(
            {
                "evaluator.py": b"class Eval: pass",
                "__pycache__/evaluator.cpython-312.pyc": b"compiled",
                "other.pyc": b"compiled",
                "other.pyo": b"optimized",
            }
        )

        with patch("azure.ai.projects.operations._patch_evaluators.ContainerClient") as MockContainerClient:
            mock_container = MagicMock()
            MockContainerClient.from_container_url.return_value = mock_container
            mock_container.__enter__ = MagicMock(return_value=mock_container)
            mock_container.__exit__ = MagicMock(return_value=False)

            ops.upload(
                name="test",
                evaluator_version={"definition": {}},
                folder=folder,
            )

            # All files should be uploaded when no patterns are provided
            assert mock_container.upload_blob.call_count == 4

    # ---------------------------------------------------------------
    # upload() - blob_uri set on evaluator version tests
    # ---------------------------------------------------------------

    def test_upload_sets_blob_uri_on_dict_evaluator_version(self):
        ops = self._create_operations()
        ops.list_versions.side_effect = ResourceNotFoundError("Not found")
        blob_uri = "https://storage.blob.core.windows.net/container-1"
        ops.start_pending_upload.return_value = self._mock_pending_upload_response(blob_uri=blob_uri)
        ops.create_version.return_value = {"name": "test", "version": "1"}

        folder = self._create_temp_folder()

        evaluator_version = {"definition": {"entry_point": "eval:Eval"}}

        with patch("azure.ai.projects.operations._patch_evaluators.ContainerClient") as MockContainerClient:
            mock_container = MagicMock()
            MockContainerClient.from_container_url.return_value = mock_container
            mock_container.__enter__ = MagicMock(return_value=mock_container)
            mock_container.__exit__ = MagicMock(return_value=False)

            ops.upload(
                name="test",
                evaluator_version=evaluator_version,
                folder=folder,
            )

            # Verify blob_uri was set in the definition
            assert evaluator_version["definition"]["blob_uri"] == blob_uri

    def test_upload_sets_blob_uri_on_model_evaluator_version(self):
        ops = self._create_operations()
        ops.list_versions.side_effect = ResourceNotFoundError("Not found")
        blob_uri = "https://storage.blob.core.windows.net/container-1"
        ops.start_pending_upload.return_value = self._mock_pending_upload_response(blob_uri=blob_uri)
        ops.create_version.return_value = {"name": "test", "version": "1"}

        folder = self._create_temp_folder()

        # Create a mock EvaluatorVersion object
        ev = MagicMock(spec=EvaluatorVersion)
        ev.definition = MagicMock(spec=CodeBasedEvaluatorDefinition)
        ev.definition.blob_uri = None

        with patch("azure.ai.projects.operations._patch_evaluators.ContainerClient") as MockContainerClient:
            mock_container = MagicMock()
            MockContainerClient.from_container_url.return_value = mock_container
            mock_container.__enter__ = MagicMock(return_value=mock_container)
            mock_container.__exit__ = MagicMock(return_value=False)

            ops.upload(
                name="test",
                evaluator_version=ev,
                folder=folder,
            )

            # Verify blob_uri was set on the model object
            assert ev.definition.blob_uri == blob_uri

    # ---------------------------------------------------------------
    # upload() - create_version call tests
    # ---------------------------------------------------------------

    def test_upload_calls_create_version_with_correct_args(self):
        ops = self._create_operations()
        ops.list_versions.side_effect = ResourceNotFoundError("Not found")
        ops.start_pending_upload.return_value = self._mock_pending_upload_response()
        ops.create_version.return_value = {"name": "my_eval", "version": "1"}

        folder = self._create_temp_folder()
        evaluator_version = {"definition": {"entry_point": "eval:Eval"}}

        with patch("azure.ai.projects.operations._patch_evaluators.ContainerClient") as MockContainerClient:
            mock_container = MagicMock()
            MockContainerClient.from_container_url.return_value = mock_container
            mock_container.__enter__ = MagicMock(return_value=mock_container)
            mock_container.__exit__ = MagicMock(return_value=False)

            result = ops.upload(
                name="my_eval",
                evaluator_version=evaluator_version,
                folder=folder,
            )

            ops.create_version.assert_called_once_with(
                name="my_eval",
                evaluator_version=evaluator_version,
                headers=_EVALUATORS_HEADERS,
            )
            assert result == {"name": "my_eval", "version": "1"}

    def test_upload_auto_increments_version(self):
        ops = self._create_operations()
        ops.list_versions.return_value = [{"version": "1"}, {"version": "2"}]
        ops.start_pending_upload.return_value = self._mock_pending_upload_response()
        ops.create_version.return_value = {"name": "my_eval", "version": "3"}

        folder = self._create_temp_folder()

        with patch("azure.ai.projects.operations._patch_evaluators.ContainerClient") as MockContainerClient:
            mock_container = MagicMock()
            MockContainerClient.from_container_url.return_value = mock_container
            mock_container.__enter__ = MagicMock(return_value=mock_container)
            mock_container.__exit__ = MagicMock(return_value=False)

            ops.upload(
                name="my_eval",
                evaluator_version={"definition": {}},
                folder=folder,
            )

            # pending_upload should be called with version "3"
            ops.start_pending_upload.assert_called_once_with(
                name="my_eval",
                version="3",
                pending_upload_request={},
                headers=_EVALUATORS_HEADERS,
            )

    # ---------------------------------------------------------------
    # upload() - error handling tests
    # ---------------------------------------------------------------

    def test_upload_raises_permission_error_on_auth_mismatch(self):
        ops = self._create_operations()
        ops.list_versions.side_effect = ResourceNotFoundError("Not found")
        ops.start_pending_upload.return_value = self._mock_pending_upload_response()

        folder = self._create_temp_folder()

        with patch("azure.ai.projects.operations._patch_evaluators.ContainerClient") as MockContainerClient:
            mock_container = MagicMock()
            MockContainerClient.from_container_url.return_value = mock_container
            mock_container.__enter__ = MagicMock(return_value=mock_container)
            mock_container.__exit__ = MagicMock(return_value=False)
            mock_container.url = "https://mystorage.blob.core.windows.net/container"

            error = HttpResponseError(message="Auth failed")
            error.error_code = "AuthorizationPermissionMismatch"
            error.response = MagicMock()
            mock_container.upload_blob.side_effect = error

            with pytest.raises(HttpResponseError, match="Storage Blob Data Contributor"):
                ops.upload(
                    name="test",
                    evaluator_version={"definition": {}},
                    folder=folder,
                )

    def test_upload_reraises_non_auth_http_errors(self):
        ops = self._create_operations()
        ops.list_versions.side_effect = ResourceNotFoundError("Not found")
        ops.start_pending_upload.return_value = self._mock_pending_upload_response()

        folder = self._create_temp_folder()

        with patch("azure.ai.projects.operations._patch_evaluators.ContainerClient") as MockContainerClient:
            mock_container = MagicMock()
            MockContainerClient.from_container_url.return_value = mock_container
            mock_container.__enter__ = MagicMock(return_value=mock_container)
            mock_container.__exit__ = MagicMock(return_value=False)

            error = HttpResponseError(message="Server error")
            error.error_code = "InternalServerError"
            mock_container.upload_blob.side_effect = error

            with pytest.raises(HttpResponseError, match="Server error"):
                ops.upload(
                    name="test",
                    evaluator_version={"definition": {}},
                    folder=folder,
                )
