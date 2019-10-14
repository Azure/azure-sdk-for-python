# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._shared.base_client import StorageAccountHostsMixin


class PathClient(StorageAccountHostsMixin):
    def __init__(
            self, account_url,  # type: str
            file_system_name,  # type: str
            path_name,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
    ):
        self._blob_client

    def generate_shared_access_signature(self):
        pass

    def create_path(self, resource_type, **kwargs):
        """
        Create directory or file
        :return:
        """
        pass

    def delete_path(self, recursive=True, lease=None, **kwargs):
        """
        Marks the specified path for deletion.
        :return:
        """
        pass

    def set_access_control(self, owner=None, group=None, permissions=None, **kwargs):
        pass

    def get_access_control(self, **kwargs):
        pass

    def rename_path(self, rename_mode='posix', **kwargs):
        pass

    def get_path_properties(self, **kwargs):
        pass

    def set_path_metadata(self, metadata=None, **kwargs):
        pass

    def set_http_headers(self, content_settings=None, **kwargs):
        pass

    def acquire_lease(self, lease_duration=-1, lease_id=None, **kwargs):
        pass
