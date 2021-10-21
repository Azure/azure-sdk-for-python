# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=super-init-not-called, too-many-lines
from .._models import FileSystemProperties
from azure.core.async_paging import AsyncPageIterator
from azure.core.exceptions import HttpResponseError
from azure.storage.blob.aio._models import ContainerPropertiesPaged

from .._deserialize import process_storage_error
from .._generated.models import Path
from .._models import PathProperties


class FileSystemPropertiesPaged(ContainerPropertiesPaged):
    """An Iterable of File System properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A file system name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str continuation_token: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.filedatalake.FileSystemProperties)

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only file systems whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of file system names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """

    def __init__(self, *args, **kwargs):
        super(FileSystemPropertiesPaged, self).__init__(
            *args,
            **kwargs
        )

    @staticmethod
    def _build_item(item):
        return FileSystemProperties._from_generated(item)  # pylint: disable=protected-access


class PathPropertiesPaged(AsyncPageIterator):
    """An Iterable of Path properties.
    :ivar str path: Filters the results to return only paths under the specified path.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str continuation_token: The continuation token to retrieve the next page of results.
    :ivar list(~azure.storage.filedatalake.PathProperties) current_page: The current page of listed results.
    :param callable command: Function to retrieve the next page of items.
    :param str path: Filters the results to return only paths under the specified path.
    :param int max_results: The maximum number of psths to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """

    def __init__(
            self, command,
            recursive,
            path=None,
            max_results=None,
            continuation_token=None,
            upn=None):
        super(PathPropertiesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.recursive = recursive
        self.results_per_page = max_results
        self.path = path
        self.upn = upn
        self.current_page = None
        self.path_list = None

    async def _get_next_cb(self, continuation_token):
        try:
            return self._command(
                self.recursive,
                continuation=continuation_token or None,
                path=self.path,
                max_results=self.results_per_page,
                upn=self.upn)
        except HttpResponseError as error:
            process_storage_error(error)

    async def _extract_data_cb(self, get_next_return):
        path_list = []
        async for path in get_next_return:
            path_list.append(path)
        self.path_list = path_list
        self.current_page = [self._build_item(item) for item in self.path_list]

        return None, self.current_page

    @staticmethod
    def _build_item(item):
        if isinstance(item, PathProperties):
            return item
        if isinstance(item, Path):
            path = PathProperties._from_generated(item)  # pylint: disable=protected-access
            return path
        return item