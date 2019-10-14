# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._shared.base_client import StorageAccountHostsMixin


class FileSystemClient(StorageAccountHostsMixin):
    def __init__(
        self, account_url,  # type: str
        file_system_name,  # type: str
        credential=None,  # type: Optional[Any]
        **kwargs  # type: Any
    ):
        self._container_client

    @classmethod
    def from_file_system_url(cls):
        pass

    def generate_shared_access_signature(self):
        pass

    def acquire_lease(
        self, lease_duration=-1,  # type: int
        lease_id=None,  # type: Optional[str]
        **kwargs
    ):
        pass

    def create_file_system(self, metadata=None, **kwargs):
        pass

    def delete_file_system(self, **kwargs):
        # type: (Any) -> None
        pass

    def get_file_system_properties(self, **kwargs):
        # type: (Any) -> FileSystemProperties
        pass

    def set_file_system_metadata(  # type: ignore
        self, metadata=None,  # type: Optional[Dict[str, str]]
        **kwargs
    ):
        pass

    def create_directory(self, **kwargs):
        pass

    def delete_directory(self, recursive=True, lease=None, **kwargs):
        pass

    def get_paths(self, directory=None, recursive=True, max_results=None, **kwargs):
        # type: (Optional[str], Optional[Any], **Any) -> ItemPaged[BlobProperties]
        pass

    def create_file(self, file, **kwargs):
        pass

    def delete_file(self, file, lease=None, **kwargs):
        pass

    def get_directory_client(self, directory):
        pass

    def get_file_client(self, file):
        pass

    def _convert_dfs_url_to_blob_url(self):
        pass
