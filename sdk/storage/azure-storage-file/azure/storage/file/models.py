# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=super-init-not-called, too-many-lines

from azure.core.paging import PageIterator
from azure.storage.file._parser import _parse_datetime_from_str
from ._shared.response_handlers import return_context_and_deserialized, process_storage_error
from ._shared.models import DictMixin, get_enum_value
from ._generated.models import StorageErrorException
from ._generated.models import Metrics as GeneratedMetrics
from ._generated.models import RetentionPolicy as GeneratedRetentionPolicy
from ._generated.models import CorsRule as GeneratedCorsRule
from ._generated.models import AccessPolicy as GenAccessPolicy
from ._generated.models import DirectoryItem


def _wrap_item(item):
    if isinstance(item, DirectoryItem):
        return {'name': item.name, 'is_directory': True}
    return {'name': item.name, 'size': item.properties.content_length, 'is_directory': False}


class Metrics(GeneratedMetrics):
    """A summary of request statistics grouped by API in hour or minute aggregates
    for files.

    All required parameters must be populated in order to send to Azure.

    :ivar str version: The version of Storage Analytics to configure.
    :ivar bool enabled: Required. Indicates whether metrics are enabled for the
        File service.
    :ivar bool include_ap_is: Indicates whether metrics should generate summary
        statistics for called API operations.
    :ivar retention_policy: Required. Determines how long the associated data should
        persist.
    :vartype retention_policy: ~azure.storage.file.RetentionPolicy
    """

    def __init__(self, **kwargs):
        self.version = kwargs.get('version', u'1.0')
        self.enabled = kwargs.get('enabled', False)
        self.include_apis = kwargs.get('include_apis')
        self.retention_policy = kwargs.get('retention_policy') or RetentionPolicy()


class RetentionPolicy(GeneratedRetentionPolicy):
    """The retention policy which determines how long the associated data should
    persist.

    All required parameters must be populated in order to send to Azure.

    :param bool enabled: Required. Indicates whether a retention policy is enabled
        for the storage service.
    :param int days: Indicates the number of days that metrics or logging or
        soft-deleted data should be retained. All data older than this value will
        be deleted.
    """

    def __init__(self, enabled=False, days=None):
        self.enabled = enabled
        self.days = days
        if self.enabled and (self.days is None):
            raise ValueError("If policy is enabled, 'days' must be specified.")


class CorsRule(GeneratedCorsRule):
    """CORS is an HTTP feature that enables a web application running under one
    domain to access resources in another domain. Web browsers implement a
    security restriction known as same-origin policy that prevents a web page
    from calling APIs in a different domain; CORS provides a secure way to
    allow one domain (the origin domain) to call APIs in another domain.

    All required parameters must be populated in order to send to Azure.

    :param list(str) allowed_origins:
        A list of origin domains that will be allowed via CORS, or "*" to allow
        all domains. The list of must contain at least one entry. Limited to 64
        origin domains. Each allowed origin can have up to 256 characters.
    :param list(str) allowed_methods:
        A list of HTTP methods that are allowed to be executed by the origin.
        The list of must contain at least one entry. For Azure Storage,
        permitted methods are DELETE, GET, HEAD, MERGE, POST, OPTIONS or PUT.
    :param list(str) allowed_headers:
        Defaults to an empty list. A list of headers allowed to be part of
        the cross-origin request. Limited to 64 defined headers and 2 prefixed
        headers. Each header can be up to 256 characters.
    :param list(str) exposed_headers:
        Defaults to an empty list. A list of response headers to expose to CORS
        clients. Limited to 64 defined headers and two prefixed headers. Each
        header can be up to 256 characters.
    :param int max_age_in_seconds:
        The number of seconds that the client/browser should cache a
        preflight response.
    """

    def __init__(self, allowed_origins, allowed_methods, **kwargs):
        self.allowed_origins = ','.join(allowed_origins)
        self.allowed_methods = ','.join(allowed_methods)
        self.allowed_headers = ','.join(kwargs.get('allowed_headers', []))
        self.exposed_headers = ','.join(kwargs.get('exposed_headers', []))
        self.max_age_in_seconds = kwargs.get('max_age_in_seconds', 0)


class AccessPolicy(GenAccessPolicy):
    """Access Policy class used by the set and get acl methods in each service.

    A stored access policy can specify the start time, expiry time, and
    permissions for the Shared Access Signatures with which it's associated.
    Depending on how you want to control access to your resource, you can
    specify all of these parameters within the stored access policy, and omit
    them from the URL for the Shared Access Signature. Doing so permits you to
    modify the associated signature's behavior at any time, as well as to revoke
    it. Or you can specify one or more of the access policy parameters within
    the stored access policy, and the others on the URL. Finally, you can
    specify all of the parameters on the URL. In this case, you can use the
    stored access policy to revoke the signature, but not to modify its behavior.

    Together the Shared Access Signature and the stored access policy must
    include all fields required to authenticate the signature. If any required
    fields are missing, the request will fail. Likewise, if a field is specified
    both in the Shared Access Signature URL and in the stored access policy, the
    request will fail with status code 400 (Bad Request).

    :param str permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :param expiry:
        The time at which the shared access signature becomes invalid.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has
        been specified in an associated stored access policy. Azure will always
        convert values to UTC. If a date is passed in without timezone info, it
        is assumed to be UTC.
    :type expiry: ~datetime.datetime or str
    :param start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. Azure will always convert values
        to UTC. If a date is passed in without timezone info, it is assumed to
        be UTC.
    :type start: ~datetime.datetime or str
    """
    def __init__(self, permission=None, expiry=None, start=None):
        self.start = start
        self.expiry = expiry
        self.permission = permission


class ContentSettings(DictMixin):
    """Used to store the content settings of a file.

    :param str content_type:
        The content type specified for the file. If no content type was
        specified, the default content type is application/octet-stream.
    :param str content_encoding:
        If the content_encoding has previously been set
        for the file, that value is stored.
    :param str content_language:
        If the content_language has previously been set
        for the file, that value is stored.
    :param str content_disposition:
        content_disposition conveys additional information about how to
        process the response payload, and also can be used to attach
        additional metadata. If content_disposition has previously been set
        for the file, that value is stored.
    :param str cache_control:
        If the cache_control has previously been set for
        the file, that value is stored.
    :param str content_md5:
        If the content_md5 has been set for the file, this response
        header is stored so that the client can check for message content
        integrity.
    """

    def __init__(
            self, content_type=None, content_encoding=None,
            content_language=None, content_disposition=None,
            cache_control=None, content_md5=None, **kwargs):

        self.content_type = content_type or kwargs.get('Content-Type')
        self.content_encoding = content_encoding or kwargs.get('Content-Encoding')
        self.content_language = content_language or kwargs.get('Content-Language')
        self.content_md5 = content_md5 or kwargs.get('Content-MD5')
        self.content_disposition = content_disposition or kwargs.get('Content-Disposition')
        self.cache_control = cache_control or kwargs.get('Cache-Control')

    @classmethod
    def _from_generated(cls, generated):
        settings = cls()
        settings.content_type = generated.properties.content_type or None
        settings.content_encoding = generated.properties.content_encoding or None
        settings.content_language = generated.properties.content_language or None
        settings.content_md5 = generated.properties.content_md5 or None
        settings.content_disposition = generated.properties.content_disposition or None
        settings.cache_control = generated.properties.cache_control or None
        return settings


class ShareProperties(DictMixin):
    """Share's properties class.

    :ivar str name:
        The name of the share.
    :ivar datetime last_modified:
        A datetime object representing the last time the share was modified.
    :ivar str etag:
        The ETag contains a value that you can use to perform operations
        conditionally.
    :ivar int quota:
        The allocated quota.
    :ivar dict metadata: A dict with name_value pairs to associate with the
        share as metadata.
    :ivar str snapshot:
        Snapshot of the share.
    """

    def __init__(self, **kwargs):
        self.name = None
        self.last_modified = kwargs.get('Last-Modified')
        self.etag = kwargs.get('ETag')
        self.quota = kwargs.get('x-ms-share-quota')
        self.metadata = kwargs.get('metadata')
        self.snapshot = None

    @classmethod
    def _from_generated(cls, generated):
        props = cls()
        props.name = generated.name
        props.last_modified = generated.properties.last_modified
        props.etag = generated.properties.etag
        props.quota = generated.properties.quota
        props.metadata = generated.metadata
        props.snapshot = generated.snapshot
        return props


class SharePropertiesPaged(PageIterator):
    """An iterable of Share properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A file name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str continuation_token: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.file.ShareProperties)

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only shares whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of share names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """
    def __init__(self, command, prefix=None, results_per_page=None, continuation_token=None):
        super(SharePropertiesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.prefix = prefix
        self.marker = None
        self.results_per_page = results_per_page
        self.location_mode = None
        self.current_page = []

    def _get_next_cb(self, continuation_token):
        try:
            return self._command(
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                prefix=self.prefix,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except StorageErrorException as error:
            process_storage_error(error)

    def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.current_page = [ShareProperties._from_generated(i) for i in self._response.share_items]  # pylint: disable=protected-access
        return self._response.next_marker or None, self.current_page


class Handle(DictMixin):
    """A listed Azure Storage handle item.

    All required parameters must be populated in order to send to Azure.

    :param handle_id: Required. XSMB service handle ID
    :type handle_id: str
    :param path: Required. File or directory name including full path starting
     from share root
    :type path: str
    :param file_id: Required. FileId uniquely identifies the file or
     directory.
    :type file_id: str
    :param parent_id: ParentId uniquely identifies the parent directory of the
     object.
    :type parent_id: str
    :param session_id: Required. SMB session ID in context of which the file
     handle was opened
    :type session_id: str
    :param client_ip: Required. Client IP that opened the handle
    :type client_ip: str
    :param open_time: Required. Time when the session that previously opened
     the handle has last been reconnected. (UTC)
    :type open_time: ~datetime.datetime
    :param last_reconnect_time: Time handle was last connected to (UTC)
    :type last_reconnect_time: ~datetime.datetime
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get('handle_id')
        self.path = kwargs.get('path')
        self.file_id = kwargs.get('file_id')
        self.parent_id = kwargs.get('parent_id')
        self.session_id = kwargs.get('session_id')
        self.client_ip = kwargs.get('client_ip')
        self.open_time = kwargs.get('open_time')
        self.last_reconnect_time = kwargs.get('last_reconnect_time')

    @classmethod
    def _from_generated(cls, generated):
        handle = cls()
        handle.id = generated.handle_id
        handle.path = generated.path
        handle.file_id = generated.file_id
        handle.parent_id = generated.parent_id
        handle.session_id = generated.session_id
        handle.client_ip = generated.client_ip
        handle.open_time = generated.open_time
        handle.last_reconnect_time = generated.last_reconnect_time
        return handle


class HandlesPaged(PageIterator):
    """An iterable of Handles.

    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str continuation_token: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.file.Handle)

    :param callable command: Function to retrieve the next page of items.
    :param int results_per_page: The maximum number of share names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """
    def __init__(self, command, results_per_page=None, continuation_token=None):
        super(HandlesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.marker = None
        self.results_per_page = results_per_page
        self.location_mode = None
        self.current_page = []

    def _get_next_cb(self, continuation_token):
        try:
            return self._command(
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except StorageErrorException as error:
            process_storage_error(error)

    def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.current_page = [Handle._from_generated(h) for h in self._response.handle_list]  # pylint: disable=protected-access
        return self._response.next_marker or None, self.current_page


class DirectoryProperties(DictMixin):
    """Directory's properties class.

    :ivar str name:
        The name of the directory.
    :ivar datetime last_modified:
        A datetime object representing the last time the directory was modified.
    :ivar str etag:
        The ETag contains a value that you can use to perform operations
        conditionally.
    :ivar bool server_encrypted:
        Whether encryption is enabled.
    :ivar dict metadata: A dict with name_value pairs to associate with the
        directory as metadata.
    """

    def __init__(self, **kwargs):
        self.name = None
        self.last_modified = kwargs.get('Last-Modified')
        self.etag = kwargs.get('ETag')
        self.server_encrypted = kwargs.get('x-ms-server-encrypted')
        self.metadata = kwargs.get('metadata')
        self.change_time = _parse_datetime_from_str(kwargs.get('x-ms-file-change-time'))
        self.creation_time = _parse_datetime_from_str(kwargs.get('x-ms-file-creation-time'))
        self.last_write_time = _parse_datetime_from_str(kwargs.get('x-ms-file-last-write-time'))
        self.file_attributes = kwargs.get('x-ms-file-attributes')
        self.permission_key = kwargs.get('x-ms-file-permission-key')
        self.file_id = kwargs.get('x-ms-file-id')
        self.parent_id = kwargs.get('x-ms-file-parent-id')

    @classmethod
    def _from_generated(cls, generated):
        props = cls()
        props.name = generated.name
        props.last_modified = generated.properties.last_modified
        props.etag = generated.properties.etag
        props.server_encrypted = generated.properties.server_encrypted
        props.metadata = generated.metadata
        return props


class DirectoryPropertiesPaged(PageIterator):
    """An iterable for the contents of a directory.

    This iterable will yield dicts for the contents of the directory. The dicts
    will have the keys 'name' (str) and 'is_directory' (bool).
    Items that are files (is_directory=False) will have an additional 'content_length' key.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A file name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str continuation_token: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(dict(str, Any))

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only directories whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of share names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """
    def __init__(self, command, prefix=None, results_per_page=None, continuation_token=None):
        super(DirectoryPropertiesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.prefix = prefix
        self.marker = None
        self.results_per_page = results_per_page
        self.location_mode = None
        self.current_page = []

    def _get_next_cb(self, continuation_token):
        try:
            return self._command(
                marker=continuation_token or None,
                prefix=self.prefix,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except StorageErrorException as error:
            process_storage_error(error)

    def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.current_page = [_wrap_item(i) for i in self._response.segment.directory_items]
        self.current_page.extend([_wrap_item(i) for i in self._response.segment.file_items])
        return self._response.next_marker or None, self.current_page


class FileProperties(DictMixin):
    """File's properties class.

    :ivar str name:
        The name of the file.
    :ivar str path:
        The path of the file.
    :ivar str share:
        The name of share.
    :ivar str snapshot:
        File snapshot.
    :ivar int content_length:
        Size of file in bytes.
    :ivar dict metadata: A dict with name_value pairs to associate with the
        file as metadata.
    :ivar str file_type:
        Type of the file.
    :ivar datetime last_modified:
        A datetime object representing the last time the file was modified.
    :ivar str etag:
        The ETag contains a value that you can use to perform operations
        conditionally.
    :ivar int size:
        Size of file in bytes.
    :ivar str content_range:
        The range of bytes.
    :ivar bool server_encrypted:
        Whether encryption is enabled.
    :ivar copy:
        The copy properties.
    :vartype copy: ~azure.storage.file.CopyProperties
    :ivar content_settings:
        The content settings for the file.
    :vartype content_settings: ~azure.storage.file.ContentSettings
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.path = None
        self.share = None
        self.snapshot = None
        self.content_length = kwargs.get('Content-Length')
        self.metadata = kwargs.get('metadata')
        self.file_type = kwargs.get('x-ms-type')
        self.last_modified = kwargs.get('Last-Modified')
        self.etag = kwargs.get('ETag')
        self.size = kwargs.get('Content-Length')
        self.content_range = kwargs.get('Content-Range')
        self.server_encrypted = kwargs.get('x-ms-server-encrypted')
        self.copy = CopyProperties(**kwargs)
        self.content_settings = ContentSettings(**kwargs)
        self.change_time = _parse_datetime_from_str(kwargs.get('x-ms-file-change-time'))
        self.creation_time = _parse_datetime_from_str(kwargs.get('x-ms-file-creation-time'))
        self.last_write_time = _parse_datetime_from_str(kwargs.get('x-ms-file-last-write-time'))
        self.file_attributes = kwargs.get('x-ms-file-attributes')
        self.permission_key = kwargs.get('x-ms-file-permission-key')
        self.file_id = kwargs.get('x-ms-file-id')
        self.parent_id = kwargs.get('x-ms-file-parent-id')

    @classmethod
    def _from_generated(cls, generated):
        props = cls()
        props.name = generated.name
        props.content_length = generated.properties.content_length
        props.metadata = generated.properties.metadata
        return props


class CopyProperties(DictMixin):
    """File Copy Properties.

    :ivar str id:
        String identifier for the last attempted Copy File operation where this file
        was the destination file. This header does not appear if this file has never
        been the destination in a Copy File operation, or if this file has been
        modified after a concluded Copy File operation.
    :ivar str source:
        URL up to 2 KB in length that specifies the source file used in the last attempted
        Copy File operation where this file was the destination file. This header does not
        appear if this file has never been the destination in a Copy File operation, or if
        this file has been modified after a concluded Copy File operation.
    :ivar str status:
        State of the copy operation identified by Copy ID, with these values:
            success:
                Copy completed successfully.
            pending:
                Copy is in progress. Check copy_status_description if intermittent,
                non-fatal errors impede copy progress but don't cause failure.
            aborted:
                Copy was ended by Abort Copy File.
            failed:
                Copy failed. See copy_status_description for failure details.
    :ivar str progress:
        Contains the number of bytes copied and the total bytes in the source in the last
        attempted Copy File operation where this file was the destination file. Can show
        between 0 and Content-Length bytes copied.
    :ivar datetime completion_time:
        Conclusion time of the last attempted Copy File operation where this file was the
        destination file. This value can specify the time of a completed, aborted, or
        failed copy attempt.
    :ivar str status_description:
        Only appears when x-ms-copy-status is failed or pending. Describes cause of fatal
        or non-fatal copy operation failure.
    :ivar bool incremental_copy:
        Copies the snapshot of the source file to a destination file.
        The snapshot is copied such that only the differential changes between
        the previously copied snapshot are transferred to the destination
    :ivar datetime destination_snapshot:
        Included if the file is incremental copy or incremental copy snapshot,
        if x-ms-copy-status is success. Snapshot time of the last successful
        incremental copy snapshot for this file.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get('x-ms-copy-id')
        self.source = kwargs.get('x-ms-copy-source')
        self.status = kwargs.get('x-ms-copy-status')
        self.progress = kwargs.get('x-ms-copy-progress')
        self.completion_time = kwargs.get('x-ms-copy-completion_time')
        self.status_description = kwargs.get('x-ms-copy-status-description')
        self.incremental_copy = kwargs.get('x-ms-incremental-copy')
        self.destination_snapshot = kwargs.get('x-ms-copy-destination-snapshot')

    @classmethod
    def _from_generated(cls, generated):
        copy = cls()
        copy.id = generated.properties.copy_id or None
        copy.status = get_enum_value(generated.properties.copy_status) or None
        copy.source = generated.properties.copy_source or None
        copy.progress = generated.properties.copy_progress or None
        copy.completion_time = generated.properties.copy_completion_time or None
        copy.status_description = generated.properties.copy_status_description or None
        copy.incremental_copy = generated.properties.incremental_copy or None
        copy.destination_snapshot = generated.properties.destination_snapshot or None
        return copy


class FileSasPermissions(object):
    """FileSasPermissions class to be used with
    generating shared access signature operations.

    :param bool read:
        Read the content, properties, metadata. Use the file as the source of a copy
        operation.
    :param bool create:
        Create a new file or copy a file to a new file.
    :param bool write:
        Create or write content, properties, metadata. Resize the file. Use the file
        as the destination of a copy operation within the same account.
    :param bool delete:
        Delete the file.
    """
    def __init__(self, read=False, create=False, write=False, delete=False):
        self.read = read
        self.create = create
        self.write = write
        self.delete = delete
        self._str = (('r' if self.read else '') +
                     ('c' if self.create else '') +
                     ('w' if self.write else '') +
                     ('d' if self.delete else ''))

    def __str__(self):
        return self._str

    @classmethod
    def from_string(cls, permission):
        p_read = 'r' in permission
        p_create = 'c' in permission
        p_write = 'w' in permission
        p_delete = 'd' in permission

        parsed = cls(p_read, p_create, p_write, p_delete)
        parsed._str = permission # pylint: disable = protected-access
        return parsed


class ShareSasPermissions(object):
    """ShareSasPermissions class to be used to be used with
    generating shared access signature and access policy operations.

    :param bool read:
        Read the content, properties or metadata of any file in the share. Use any
        file in the share as the source of a copy operation.
    :param bool write:
        For any file in the share, create or write content, properties or metadata.
        Resize the file. Use the file as the destination of a copy operation within
        the same account.
        Note: You cannot grant permissions to read or write share properties or
        metadata with a service SAS. Use an account SAS instead.
    :param bool delete:
        Delete any file in the share.
        Note: You cannot grant permissions to delete a share with a service SAS. Use
        an account SAS instead.
    :param bool list:
        List files and directories in the share.
    """
    def __init__(self, read=False, write=False, delete=False, list=False):  # pylint: disable=redefined-builtin
        self.read = read
        self.write = write
        self.delete = delete
        self.list = list
        self._str = (('r' if self.read else '') +
                     ('w' if self.write else '') +
                     ('d' if self.delete else '') +
                     ('l' if self.list else ''))


    def __str__(self):
        return self._str

    @classmethod
    def from_string(cls, permission):
        p_read = 'r' in permission
        p_write = 'w' in permission
        p_delete = 'd' in permission
        p_list = 'l' in permission

        parsed = cls(p_read, p_write, p_delete, p_list)
        parsed._str = permission # pylint: disable = protected-access
        return parsed

class NTFSAttributes(object):
    """
    Valid set of attributes to set for file or directory.
    To set attribute for directory, 'Directory' should always be enabled except setting 'None' for directory.

    :ivar bool read_only:
        Enable/disable 'ReadOnly' attribute for DIRECTORY or FILE
    :ivar bool hidden:
        Enable/disable 'Hidden' attribute for DIRECTORY or FILE
    :ivar bool system:
        Enable/disable 'System' attribute for DIRECTORY or FILE
    :ivar bool none:
        Enable/disable 'None' attribute for DIRECTORY or FILE to clear all attributes of FILE/DIRECTORY
    :ivar bool directory:
        Enable/disable 'Directory' attribute for DIRECTORY
    :ivar bool archive:
        Enable/disable 'Archive' attribute for DIRECTORY or FILE
    :ivar bool temporary:
        Enable/disable 'Temporary' attribute for FILE
    :ivar bool offline:
        Enable/disable 'Offline' attribute for DIRECTORY or FILE
    :ivar bool not_content_indexed:
        Enable/disable 'NotContentIndexed' attribute for DIRECTORY or FILE
    :ivar bool no_scrub_data:
        Enable/disable 'NoScrubData' attribute for DIRECTORY or FILE
    """
    def __init__(self, read_only=False, hidden=False, system=False, none=False, directory=False, archive=False,
                 temporary=False, offline=False, not_content_indexed=False, no_scrub_data=False, _str=None):
        if not _str:
            _str = ''
        self.read_only = read_only or ('ReadOnly' in _str)
        self.hidden = hidden or ('Hidden' in _str)
        self.system = system or ('System' in _str)
        self.none = none or ('None' in _str)
        self.directory = directory or ('Directory' in _str)
        self.archive = archive or ('Archive' in _str)
        self.temporary = temporary or ('Temporary' in _str)
        self.offline = offline or ('Offline' in _str)
        self.not_content_indexed = not_content_indexed or ('NotContentIndexed' in _str)
        self.no_scrub_data = no_scrub_data or ('NoScrubData' in _str)

    def __or__(self, other):
        return NTFSAttributes(_str=str(self) + str(other))

    def __add__(self, other):
        return NTFSAttributes(_str=str(self) + str(other))

    def __str__(self):
        concatenated_params = (('ReadOnly|' if self.read_only else '') +
                               ('Hidden|' if self.hidden else '') +
                               ('System|' if self.system else '') +
                               ('None|' if self.none else '') +
                               ('Directory|' if self.directory else '') +
                               ('Archive|' if self.archive else '') +
                               ('Temporary|' if self.temporary else '') +
                               ('Offline|' if self.offline else '') +
                               ('NotContentIndexed|' if self.not_content_indexed else '') +
                               ('NoScrubData|' if self.no_scrub_data else ''))

        return concatenated_params.strip('|')


NTFSAttributes.READ_ONLY = NTFSAttributes(read_only=True)
NTFSAttributes.HIDDEN = NTFSAttributes(hidden=True)
NTFSAttributes.SYSTEM = NTFSAttributes(system=True)
NTFSAttributes.NONE = NTFSAttributes(none=True)
NTFSAttributes.DIRECTORY = NTFSAttributes(directory=True)
NTFSAttributes.ARCHIVE = NTFSAttributes(archive=True)
NTFSAttributes.TEMPORARY = NTFSAttributes(temporary=True)
NTFSAttributes.OFFLINE = NTFSAttributes(offline=True)
NTFSAttributes.NOT_CONTENT_INDEXED = NTFSAttributes(not_content_indexed=True)
NTFSAttributes.NO_SCRUB_DATA = NTFSAttributes(no_scrub_data=True)
