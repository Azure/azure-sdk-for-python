# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._shared.base_client import StorageAccountHostsMixin
from .file_system_client import FileSystemClient


class DataLakeServiceClient(StorageAccountHostsMixin):
    def __init__(
            self, account_url,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
    ):
        self._blob_service_client

    def get_file_systems(self, name_starts_with=None,  # type: Optional[str]
                         include_metadata=False,  # type: Optional[bool]
                         **kwargs):
        # type: (...) -> ItemPaged[FileSystemProperties]
        pass

    def create_file_system(self, name,  # type: str
                           metadata=None,  # type: Optional[Dict[str, str]]
                           **kwargs):
        # type: (...) -> FileSystemClient
        pass

    def delete_file_system(self, file_system, **kwargs):
        pass

    def get_directory_client(self, file_system, directory):
        pass

    def get_file_client(self, file_system, file):
        pass

