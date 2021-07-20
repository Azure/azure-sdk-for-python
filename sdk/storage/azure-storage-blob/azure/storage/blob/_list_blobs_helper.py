# pylint: disable=too-many-lines
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.paging import PageIterator, ItemPaged
from azure.core.exceptions import HttpResponseError

from ._deserialize import get_blob_properties_from_generated_code, parse_tags
from ._generated.models import BlobItemInternal, BlobPrefix as GenBlobPrefix, FilterBlobItem
from ._models import BlobProperties, FilteredBlob
from ._shared.models import DictMixin
from ._shared.xml_deserialization import unpack_xml_content
from ._shared.response_handlers import return_context_and_deserialized, process_storage_error


def deserialize_list_result(pipeline_response, _, headers):
    payload = unpack_xml_content(pipeline_response.http_response)
    location = pipeline_response.http_response.location_mode
    return location, payload

def load_xml_string(element, name):
    node = element.find(name)
    if node is None or not node.text:
        return None
    return node.text

def load_xml_int(element, name):
    node = element.find(name)
    if node is None or not node.text:
        return None
    return int(node.text)

def load_xml_bool(element, name):
    node = load_xml_string(element, name)
    if node and node.lower() == 'true':
        return True
    return False


def load_single_node(element, name):
    return element.find(name)


def load_many_nodes(element, name, wrapper=None):
    if wrapper:
        element = load_single_node(element, wrapper)
    return list(element.findall(name))


def blob_properties_from_xml(element, select, deserializer):
    if not select:
        generated = deserializer.deserialize_data(element, 'BlobItemInternal')
        return get_blob_properties_from_generated_code(generated)
    blob = BlobProperties()
    if 'name' in select:
        blob.name = load_xml_string(element, 'Name')
    if 'deleted' in select:
        blob.deleted =  load_xml_bool(element, 'Deleted')
    if 'snapshot' in select:
        blob.snapshot = load_xml_string(element, 'Snapshot')
    if 'version' in select:
        blob.version_id = load_xml_string(element, 'VersionId')
        blob.is_current_version = load_xml_bool(element, 'IsCurrentVersion')
    return blob


class BlobPropertiesPaged(PageIterator):
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
    :param str container: The name of the container.
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
            container=None,
            prefix=None,
            results_per_page=None,
            select=None,
            deserializer=None,
            continuation_token=None,
            delimiter=None,
            location_mode=None):
        super(BlobPropertiesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self._deserializer = deserializer
        self.service_endpoint = None
        self.prefix = prefix
        self.marker = None
        self.results_per_page = results_per_page
        self.select = select
        self.container = container
        self.delimiter = delimiter
        self.current_page = None
        self.location_mode = location_mode

    def _get_next_cb(self, continuation_token):
        try:
            return self._command(
                prefix=self.prefix,
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=deserialize_list_result,
                use_location=self.location_mode)
        except HttpResponseError as error:
            process_storage_error(error)

    def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.service_endpoint = self._response.get('ServiceEndpoint')
        self.prefix = load_xml_string(self._response, 'Prefix')
        self.marker = load_xml_string(self._response, 'Marker')
        self.results_per_page = load_xml_int(self._response, 'MaxResults')
        self.container = self._response.get('ContainerName')

        blobs = load_many_nodes(self._response, 'Blob', wrapper='Blobs')
        self.current_page = [self._build_item(blob) for blob in blobs]

        next_marker = load_xml_string(self._response, 'NextMarker')
        return next_marker or None, self.current_page

    def _build_item(self, item):
        blob = blob_properties_from_xml(item, self.select, self._deserializer)
        blob.container = self.container
        return blob


class BlobPrefixPaged(BlobPropertiesPaged):
    def __init__(self, *args, **kwargs):
        super(BlobPrefixPaged, self).__init__(*args, **kwargs)
        self.name = self.prefix

    def _extract_data_cb(self, get_next_return):
        continuation_token, _ = super(BlobPrefixPaged, self)._extract_data_cb(get_next_return)

        blob_prefixes = load_many_nodes(self._response, 'BlobPrefix', wrapper='Blobs')
        blob_prefixes = [self._build_prefix(blob) for blob in blob_prefixes]

        self.current_page = blob_prefixes + self.current_page
        self.delimiter = load_xml_string(self._response, 'Delimiter')

        return continuation_token, self.current_page

    def _build_prefix(self, item):
        return BlobPrefix(
            self._command,
            container=self.container,
            prefix=load_xml_string(item, 'Name'),
            results_per_page=self.results_per_page,
            location_mode=self.location_mode,
            select=self.select,
            deserializer=self._deserializer,
            delimiter=self.delimiter
        )


class BlobPrefix(ItemPaged, DictMixin):
    """An Iterable of Blob properties.

    Returned from walk_blobs when a delimiter is used.
    Can be thought of as a virtual blob directory.

    :ivar str name: The prefix, or "directory name" of the blob.
    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A blob name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str next_marker: The continuation token to retrieve the next page of results.
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
    :param str marker: An opaque continuation token.
    :param str delimiter:
        Used to capture blobs whose names begin with the same substring up to
        the appearance of the delimiter character. The delimiter may be a single
        character or a string.
    :param location_mode: Specifies the location the request should be sent to.
        This mode only applies for RA-GRS accounts which allow secondary read access.
        Options include 'primary' or 'secondary'.
    """
    def __init__(self, *args, **kwargs):
        super(BlobPrefix, self).__init__(*args, page_iterator_class=BlobPrefixPaged, **kwargs)
        self.name = kwargs.get('prefix')
        self.prefix = kwargs.get('prefix')
        self.results_per_page = kwargs.get('results_per_page')
        self.container = kwargs.get('container')
        self.delimiter = kwargs.get('delimiter')
        self.location_mode = kwargs.get('location_mode')


class FilteredBlobPaged(PageIterator):
    """An Iterable of Blob properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A blob name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str continuation_token: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.blob.FilteredBlob)
    :ivar str container: The container that the blobs are listed from.

    :param callable command: Function to retrieve the next page of items.
    :param str container: The name of the container.
    :param int results_per_page: The maximum number of blobs to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    :param location_mode: Specifies the location the request should be sent to.
        This mode only applies for RA-GRS accounts which allow secondary read access.
        Options include 'primary' or 'secondary'.
    """
    def __init__(
            self, command,
            container=None,
            results_per_page=None,
            continuation_token=None,
            location_mode=None):
        super(FilteredBlobPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.marker = continuation_token
        self.results_per_page = results_per_page
        self.container = container
        self.current_page = None
        self.location_mode = location_mode

    def _get_next_cb(self, continuation_token):
        try:
            return self._command(
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except HttpResponseError as error:
            process_storage_error(error)

    def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.service_endpoint = self._response.service_endpoint
        self.marker = self._response.next_marker
        self.current_page = [self._build_item(item) for item in self._response.blobs]

        return self._response.next_marker or None, self.current_page

    @staticmethod
    def _build_item(item):
        if isinstance(item, FilterBlobItem):
            tags = parse_tags(item.tags)
            blob = FilteredBlob(name=item.name, container_name=item.container_name, tags=tags)
            return blob
        return item
