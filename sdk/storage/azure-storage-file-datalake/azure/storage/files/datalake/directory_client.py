# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._path_client import PathClient


class DirectoryClient(PathClient):
    def __init__(
        self, account_url,  # type: str
        file_system_name,  # type: str
        directory_name,  # type: str
        credential=None,  # type: Optional[Any]
        **kwargs  # type: Any
    ):
        self._blob_client

    def generate_shared_access_signature(self):
        # ???
        pass

    def create_directory(self, **kwargs):
        """
        Create directory
        :return:
        """
        pass

    def delete_directory(self, recursive=True, lease=None, **kwargs):
        # type: (...) -> ItemPaged[Response]
        """
        Marks the specified directory for deletion.
        :return:
        """
        pass

    def create_sub_directory(self, **kwargs):
        pass

    def delete_sub_directory(self, recursive=True, lease=None, **kwargs):
        pass

    def get_file_client(self, file):
        pass

    def get_sub_directory_client(self, sub_directory):
        pass

    def _convert_dfs_url_to_blob_url(self):
        pass
