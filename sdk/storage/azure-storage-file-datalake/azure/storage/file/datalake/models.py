# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=super-init-not-called, too-many-lines
from azure.core.paging import PageIterator
from azure.storage.blob import ContainerProperties, LeaseProperties, ContentSettings, ContainerSasPermissions, \
    BlobSasPermissions, AccessPolicy, BlobProperties
from azure.storage.blob._generated.models import StorageErrorException
from azure.storage.blob._models import ContainerPropertiesPaged, BlobPropertiesPaged
from azure.storage.blob._shared.response_handlers import process_storage_error, return_context_and_deserialized
from azure.storage.file.datalake._deserialize import return_headers_and_deserialized_path_list
from azure.storage.file.datalake._generated.models import Path


class FileSystemProperties(ContainerProperties):
    def __init__(self, **kwargs):
        super(FileSystemProperties, self).__init__(
            **kwargs
        )


class FileSystemPropertiesPaged(ContainerPropertiesPaged):
    def __init__(self, *args, **kwargs):
        super(FileSystemPropertiesPaged, self).__init__(
            *args,
            **kwargs
        )

    @staticmethod
    def _build_item(item):
        return FileSystemProperties._from_generated(item)  # pylint: disable=protected-access


class DirectoryProperties(BlobProperties):
    def __init__(self, **kwargs):
        super(DirectoryProperties, self).__init__(
            **kwargs
        )


class PathProperties(object):
    def __init__(self, **kwargs):
        super(PathProperties, self).__init__(
            **kwargs
        )
        self.name = kwargs.pop('name', None)
        self.owner = kwargs.get('owner', None)
        self.group = kwargs.get('group', None)
        self.permissions = kwargs.get('permissions', None)
        self.last_modified = kwargs.get('last_modified', None)
        self.is_directory = kwargs.get('is_directory', None)
        self.etag = kwargs.get('etag', None)
        self.content_length = kwargs.get('content_length', None)

    @classmethod
    def _from_generated(cls, generated):
        path_prop = PathProperties()
        path_prop.name = generated.name
        path_prop.owner = generated.owner
        path_prop.group = generated.group
        path_prop.permissions = generated.permissions
        path_prop.last_modified = generated.last_modified
        path_prop.is_directory = generated.is_directory
        path_prop.etag =generated.additional_properties.get('etag')
        path_prop.content_length = generated.content_length
        return path_prop


class PathPropertiesPaged(PageIterator):
    """An Iterable of Blob properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A blob name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str continuation_token: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.blob.BlobProperties)
    :ivar str container: The container that the blobs are listed from.
    :ivar str delimiter: A delimiting character used for hierarchy listing.

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only blobs whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of blobs to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    :param str delimiter:
        Used to capture blobs whose names begin with the same substring up to
        the appearance of the delimiter character. The delimiter may be a single
        character or a string.
    :param location_mode: Specifies the location the request should be sent to.
        This mode only applies for RA-GRS accounts which allow secondary read access.
        Options include 'primary' or 'secondary'.
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
        self.service_endpoint = None
        self.recursive = recursive
        self.marker = None
        self.results_per_page = max_results
        self.path = path
        self.upn = upn
        self.current_page = None

    def _get_next_cb(self, continuation_token):
        try:
            return self._command(
                self.recursive,
                continuation=continuation_token or None,
                path=self.path,
                max_results=self.results_per_page,
                upn=self.upn,
                cls=return_headers_and_deserialized_path_list)
        except StorageErrorException as error:
            process_storage_error(error)

    def _extract_data_cb(self, get_next_return):
        self.path_list, self._response = get_next_return
        self.continuation = self._response['continuation']
        self.current_page = [self._build_item(item) for item in self.path_list]

        return self.continuation or None, self.current_page

    def _build_item(self, item):
        if isinstance(item, PathProperties):
            return item
        if isinstance(item, Path):
            path = PathProperties._from_generated(item)  # pylint: disable=protected-access
            return path
        return item

class LeaseProperties(LeaseProperties):
    def __init__(self, **kwargs):
        super(LeaseProperties, self).__init__(
            **kwargs
        )


class ContentSettings(ContentSettings):
    def __init__(
            self, content_type=None, content_encoding=None,
            content_language=None, content_disposition=None,
            cache_control=None, content_md5=None, **kwargs):
        super(ContentSettings, self).__init__(
            content_type=content_type,
            content_encoding=content_encoding,
            content_language=content_language,
            content_disposition=content_disposition,
            cache_control=cache_control,
            content_md5=content_md5,
            **kwargs
        )


class AccessPolicy(AccessPolicy):
    def __init__(self, permission=None, expiry=None, start=None):
        super(AccessPolicy, self).__init__(
            start=start,
            expiry=expiry,
            permission=permission
        )


class FileSystemSasPermissions(ContainerSasPermissions):
    def __init__(self, **kwargs):
        super(FileSystemSasPermissions, self).__init__(
            **kwargs
        )


class PathSasPermissions(BlobSasPermissions):
    def __init__(self, **kwargs):
        super(PathSasPermissions, self).__init__(
            **kwargs
        )


class LocationMode(object):
    """
    Specifies the location the request should be sent to. This mode only applies
    for RA-GRS accounts which allow secondary read access. All other account types
    must use PRIMARY.
    """

    PRIMARY = 'primary'  #: Requests should be sent to the primary location.
    SECONDARY = 'secondary'  #: Requests should be sent to the secondary location, if possible.