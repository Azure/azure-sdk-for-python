# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=super-init-not-called, too-many-lines

from azure.core.paging import Paged
from ._shared.utils import (
    decode_base64,
    return_context_and_deserialized,
    process_storage_error)

from ._shared.models import DictMixin, get_enum_value
from ._generated.models import StorageErrorException


class ShareProperties(DictMixin):
    """Share's properties class.
    :param datetime last_modified:
        A datetime object representing the last time the share was modified.
    :param str etag:
        The ETag contains a value that you can use to perform operations
        conditionally.
    :param int quota:
        The allocated quota.
    :param str public_access: Specifies whether data in the share may be accessed
        publicly and the level of access.
    :param bool has_immutability_policy:
        Represents whether the share has an immutability policy.
    :param bool has_legal_hold:
        Represents whether the share has a legal hold.
    :param dict metadata: A dict with name_value pairs to associate with the
        share as metadata.
    """

    def __init__(self, **kwargs):
        self.name = None
        self.last_modified = kwargs.get('Last-Modified')
        self.etag = kwargs.get('ETag')
        self.quota = kwargs.get('quota')
        self.metadata = kwargs.get('metadata')

    @classmethod
    def _from_generated(cls, generated):
        props = cls()
        props.name = generated.name
        props.last_modified = generated.properties.last_modified
        props.etag = generated.properties.etag
        props.quota = generated.properties.quota
        props.metadata = generated.metadata
        return props


class SharePropertiesPaged(Paged):
    """Share properties paged.
    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only shares whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of share names to retrieve per
        call.
    :param str marker: An opaque continuation token.
    """
    def __init__(self, command, prefix=None, results_per_page=None, marker=None, **kwargs):
        super(SharePropertiesPaged, self).__init__(command, None)
        self.service_endpoint = None
        self.prefix = prefix
        self.current_marker = None
        self.results_per_page = results_per_page
        self.next_marker = marker or ""
        self.location_mode = None

    def _advance_page(self):
        # type: () -> List[Model]
        """Force moving the cursor to the next azure call.
        This method is for advanced usage, iterator protocol is prefered.
        :raises: StopIteration if no further page
        :return: The current page list
        :rtype: list
        """
        if self.next_marker is None:
            raise StopIteration("End of paging")
        self._current_page_iter_index = 0
        try:
            self.location_mode, self._response = self._get_next(
                marker=self.next_marker or None,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except StorageErrorException as error:
            process_storage_error(error)

        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.current_marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.current_page = self._response.share_items
        self.next_marker = self._response.next_marker or None
        return self.current_page

    def __next__(self):
        item = super(SharePropertiesPaged, self).__next__()
        if isinstance(item, ShareProperties):
            return item
        return ShareProperties._from_generated(item)  # pylint: disable=protected-access

    next = __next__

class DirectoryProperties(DictMixin):
    """Directory's properties class.
    :param datetime last_modified:
        A datetime object representing the last time the directory was modified.
    :param str etag:
        The ETag contains a value that you can use to perform operations
        conditionally.
    :param dict metadata: A dict with name_value pairs to associate with the
        directory as metadata.
    """

    def __init__(self, **kwargs):
        self.name = None
        self.last_modified = kwargs.get('Last-Modified')
        self.etag = kwargs.get('ETag')
        self.is_server_encrypted = kwargs.get('is_server_encrypted')
        self.metadata = kwargs.get('metadata')

    @classmethod
    def _from_generated(cls, generated):
        props = cls()
        props.name = generated.name
        props.last_modified = generated.properties.last_modified
        props.etag = generated.properties.etag
        props.is_server_encrypted = generated.properties.is_server_encrypted
        props.metadata = generated.metadata
        return props

class DirectoryPropertiesPaged(Paged):
    """Directory properties paged.
    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only directors whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of share names to retrieve per
        call.
    :param str marker: An opaque continuation token.
    """
    def __init__(self, command, prefix=None, results_per_page=None, marker=None, **kwargs):
        super(DirectoryPropertiesPaged, self).__init__(command, None)
        self.service_endpoint = None
        self.prefix = prefix
        self.current_marker = None
        self.results_per_page = results_per_page
        self.next_marker = marker or ""
        self.location_mode = None

    def _advance_page(self):
        # type: () -> List[Model]
        """Force moving the cursor to the next azure call.
        This method is for advanced usage, iterator protocol is prefered.
        :raises: StopIteration if no further page
        :return: The current page list
        :rtype: list
        """
        if self.next_marker is None:
            raise StopIteration("End of paging")
        self._current_page_iter_index = 0
        try:
            self.location_mode, self._response = self._get_next(
                marker=self.next_marker or None,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except StorageErrorException as error:
            process_storage_error(error)

        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.current_marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.current_page = self._response.directory_items
        self.next_marker = self._response.next_marker or None
        return self.current_page

    def __next__(self):
        item = super(DirectoryPropertiesPaged, self).__next__()
        if isinstance(item, DirectoryProperties):
            return item
        return DirectoryProperties._from_generated(item)  # pylint: disable=protected-access

    next = __next__

class FileProperty(DictMixin):
    """File's properties class.
    :param datetime last_modified:
        A datetime object representing the last time the file was modified.
    :param str etag:
        The ETag contains a value that you can use to perform operations
        conditionally.
    :param int quota:
        The allocated quota.
    :param str public_access: Specifies whether data in the file may be accessed
        publicly and the level of access.
    :param bool has_immutability_policy:
        Represents whether the file has an immutability policy.
    :param bool has_legal_hold:
        Represents whether the file has a legal hold.
    :param dict metadata: A dict with name_value pairs to associate with the
        file as metadata.
    """

    def __init__(self, **kwargs):
        self.name = None
        self.content_length = kwargs.get('content_length')
        self.metadata = kwargs.get('metadata')

    @classmethod
    def _from_generated(cls, generated):
        props = cls()
        props.name = generated.name
        props.content_length = generated.properties.content_length
        props.metadata = generated.properties.metadata
        return props
