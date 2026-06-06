from unittest.mock import MagicMock, patch

import pytest

from azure.ai.ml.exceptions import MlException

_CLOUD = {"storage_endpoint": "core.windows.net"}


def _named(name, is_directory=False):
    item = MagicMock()
    item.name = name
    item.is_directory = is_directory
    return item


@pytest.mark.unittest
class TestStorageDownloadTraversal:
    """Server-controlled blob/file names with ``..`` segments must not escape the destination."""

    def test_blob_download_rejects_path_traversal(self, tmp_path):
        from azure.ai.ml._artifacts._blob_storage_helper import BlobStorageClient

        with patch("azure.ai.ml._artifacts._blob_storage_helper.BlobServiceClient"):
            client = BlobStorageClient(
                credential="cred", account_url="https://acct.blob.core.windows.net", container_name="c"
            )
        client.container_client = MagicMock()
        client.container_client.list_blobs.return_value = [_named("asset/../escaped.txt")]
        blob_content = client.container_client.download_blob.return_value
        blob_content.size = 1
        blob_content.content_as_bytes.return_value = b"data"

        dest = tmp_path / "dest"
        dest.mkdir()
        with patch("azure.ai.ml._artifacts._blob_storage_helper._blob_is_hdi_folder", return_value=False), patch(
            "azure.ai.ml._artifacts._blob_storage_helper._get_cloud_details", return_value=_CLOUD
        ):
            with pytest.raises(MlException):
                client.download(starts_with="asset/", destination=str(dest))
        assert not (tmp_path / "escaped.txt").exists()

    def test_gen2_download_rejects_path_traversal(self, tmp_path):
        from azure.ai.ml._artifacts._gen2_storage_helper import Gen2StorageClient

        with patch("azure.ai.ml._artifacts._gen2_storage_helper.DataLakeServiceClient"):
            client = Gen2StorageClient(
                credential="cred", file_system="fs", account_url="https://acct.dfs.core.windows.net"
            )
        client.file_system_client = MagicMock()
        client.file_system_client.get_paths.return_value = [_named("asset/../escaped.txt")]
        file_client = client.file_system_client.get_file_client.return_value
        file_client.get_file_properties.return_value.size = 1
        file_client.download_file.return_value.readall.return_value = b"data"

        dest = tmp_path / "dest"
        dest.mkdir()
        with patch("azure.ai.ml._artifacts._gen2_storage_helper._get_cloud_details", return_value=_CLOUD):
            with pytest.raises(MlException):
                client.download(starts_with="asset/", destination=str(dest))
        assert not (tmp_path / "escaped.txt").exists()

    def test_fileshare_recursive_download_rejects_path_traversal(self, tmp_path):
        from azure.ai.ml._artifacts._fileshare_storage_helper import recursive_download

        client = MagicMock()
        client.list_directories_and_files.return_value = [{"name": "../escaped.txt", "is_directory": False}]
        client.get_file_client.return_value.download_file.return_value.readall.return_value = b"data"

        dest = tmp_path / "dest"
        dest.mkdir()
        with pytest.raises(MlException):
            recursive_download(client, destination=str(dest), max_concurrency=1)
        assert not (tmp_path / "escaped.txt").exists()
