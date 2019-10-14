# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._shared.base_client import StorageAccountHostsMixin


class FileClient(StorageAccountHostsMixin):
    def __init__(
        self, account_url,  # type: str
        file_system_name,  # type: str
        file_directory, # type: str
        file_name,  # type: str
        credential=None,  # type: Optional[Any]
        **kwargs  # type: Any
    ):
        self._blob_client

    def generate_shared_access_signature(self):
        # ???
        pass

    def create_file(self, **kwargs):
        """
        Create directory or file
        :return:
        """
        pass

    def delete_file(self, lease=None, **kwargs):
        # type: (...) -> None
        """
        Marks the specified path for deletion.
        :return:
        """
        pass

    def append_data(self, body, position=None, content_length=None, **kwargs):
        pass

    def flush_data(self, timeout=None, position=None, retain_uncommitted_data=None,
                   close=None, content_length=None, **kwargs):
        pass

    def read_file(self, offset=None, length=None, **kwargs):
        # type: (Optional[int], Optional[int], bool, **Any) -> Iterable[bytes]
        """
        Download a file from the service, including its metadata and properties
        :return:
        """
        pass

    def _convert_dfs_url_to_blob_url(self):
        pass
