# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=super-init-not-called

from typing import List # pylint: disable=unused-import
from azure.core.paging import PageIterator
from ._shared.response_handlers import return_context_and_deserialized, process_storage_error
from ._shared.models import DictMixin
from ._generated.models import StorageErrorException
from ._generated.models import AccessPolicy as GenAccessPolicy
from ._generated.models import Logging as GeneratedLogging
from ._generated.models import Metrics as GeneratedMetrics
from ._generated.models import RetentionPolicy as GeneratedRetentionPolicy
from ._generated.models import CorsRule as GeneratedCorsRule


class Logging(GeneratedLogging):
    """Azure Analytics Logging settings.

    All required parameters must be populated in order to send to Azure.

    :ivar str version: Required. The version of Storage Analytics to configure.
    :ivar bool delete: Required. Indicates whether all delete requests should be logged.
    :ivar bool read: Required. Indicates whether all read requests should be logged.
    :ivar bool write: Required. Indicates whether all write requests should be logged.
    :ivar retention_policy: Required.
        The retention policy for the metrics.
    :vartype retention_policy: ~azure.storage.queue.models.RetentionPolicy
    """

    def __init__(self, **kwargs):
        self.version = kwargs.get('version', u'1.0')
        self.delete = kwargs.get('delete', False)
        self.read = kwargs.get('read', False)
        self.write = kwargs.get('write', False)
        self.retention_policy = kwargs.get('retention_policy') or RetentionPolicy()


class Metrics(GeneratedMetrics):
    """A summary of request statistics grouped by API in hour or minute aggregates.

    All required parameters must be populated in order to send to Azure.

    :ivar str version: The version of Storage Analytics to configure.
    :ivar bool enabled: Required. Indicates whether metrics are enabled for the service.
    :ivar bool include_ap_is: Indicates whether metrics should generate summary
        statistics for called API operations.
    :ivar retention_policy: Required.
        The retention policy for the metrics.
    :vartype retention_policy: ~azure.storage.queue.models.RetentionPolicy
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
    :param int max_age_in_seconds:
        The number of seconds that the client/browser should cache a
        pre-flight response.
    :param list(str) exposed_headers:
        Defaults to an empty list. A list of response headers to expose to CORS
        clients. Limited to 64 defined headers and two prefixed headers. Each
        header can be up to 256 characters.
    :param list(str) allowed_headers:
        Defaults to an empty list. A list of headers allowed to be part of
        the cross-origin request. Limited to 64 defined headers and 2 prefixed
        headers. Each header can be up to 256 characters.
    """

    def __init__(self, allowed_origins, allowed_methods, **kwargs):
        self.allowed_origins = ','.join(allowed_origins)
        self.allowed_methods = ','.join(allowed_methods)
        self.allowed_headers = ','.join(kwargs.get('allowed_headers', []))
        self.exposed_headers = ','.join(kwargs.get('exposed_headers', []))
        self.max_age_in_seconds = kwargs.get('max_age_in_seconds', 0)


class AccessPolicy(GenAccessPolicy):
    """Access Policy class used by the set and get access policy methods.

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
    :type expiry: datetime or str
    :param start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. Azure will always convert values
        to UTC. If a date is passed in without timezone info, it is assumed to
        be UTC.
    :type start: datetime or str
    """

    def __init__(self, permission=None, expiry=None, start=None):
        self.start = start
        self.expiry = expiry
        self.permission = permission


class QueueMessage(DictMixin):
    """Queue message class.

    :ivar str id:
        A GUID value assigned to the message by the Queue service that
        identifies the message in the queue. This value may be used together
        with the value of pop_receipt to delete a message from the queue after
        it has been retrieved with the receive messages operation.
    :ivar date insertion_time:
        A UTC date value representing the time the messages was inserted.
    :ivar date expiration_time:
        A UTC date value representing the time the message expires.
    :ivar int dequeue_count:
        Begins with a value of 1 the first time the message is received. This
        value is incremented each time the message is subsequently received.
    :param obj content:
        The message content. Type is determined by the decode_function set on
        the service. Default is str.
    :ivar str pop_receipt:
        A receipt str which can be used together with the message_id element to
        delete a message from the queue after it has been retrieved with the receive
        messages operation. Only returned by receive messages operations. Set to
        None for peek messages.
    :ivar date time_next_visible:
        A UTC date value representing the time the message will next be visible.
        Only returned by receive messages operations. Set to None for peek messages.
    """

    def __init__(self, content=None):
        self.id = None
        self.insertion_time = None
        self.expiration_time = None
        self.dequeue_count = None
        self.content = content
        self.pop_receipt = None
        self.time_next_visible = None

    @classmethod
    def _from_generated(cls, generated):
        message = cls(content=generated.message_text)
        message.id = generated.message_id
        message.insertion_time = generated.insertion_time
        message.expiration_time = generated.expiration_time
        message.dequeue_count = generated.dequeue_count
        if hasattr(generated, 'pop_receipt'):
            message.pop_receipt = generated.pop_receipt
            message.time_next_visible = generated.time_next_visible
        return message


class MessagesPaged(PageIterator):
    """An iterable of Queue Messages.

    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.queue.models.QueueMessage)

    :param callable command: Function to retrieve the next page of items.
    :param int results_per_page: The maximum number of messages to retrieve per
        call.
    """
    def __init__(self, command, results_per_page=None, continuation_token=None):
        if continuation_token is not None:
            raise ValueError("This operation does not support continuation token")

        super(MessagesPaged, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
        )
        self._command = command
        self.results_per_page = results_per_page

    def _get_next_cb(self, continuation_token):
        try:
            return self._command(number_of_messages=self.results_per_page)
        except StorageErrorException as error:
            process_storage_error(error)

    def _extract_data_cb(self, messages): # pylint: disable=no-self-use
        # There is no concept of continuation token, so raising on my own condition
        if not messages:
            raise StopIteration("End of paging")
        return "TOKEN_IGNORED", [QueueMessage._from_generated(q) for q in messages]  # pylint: disable=protected-access


class QueueProperties(DictMixin):
    """Queue Properties.

    :ivar str name: The name of the queue.
    :ivar metadata:
        A dict containing name-value pairs associated with the queue as metadata.
        This var is set to None unless the include=metadata param was included
        for the list queues operation. If this parameter was specified but the
        queue has no metadata, metadata will be set to an empty dictionary.
    :vartype metadata: dict(str, str)
    """

    def __init__(self, **kwargs):
        self.name = None
        self.metadata = kwargs.get('metadata')
        self.approximate_message_count = kwargs.get('x-ms-approximate-messages-count')

    @classmethod
    def _from_generated(cls, generated):
        props = cls()
        props.name = generated.name
        props.metadata = generated.metadata
        return props


class QueuePropertiesPaged(PageIterator):
    """An iterable of Queue properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A queue name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str next_marker: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.queue.models.QueueProperties)

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only queues whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of queue names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """
    def __init__(self, command, prefix=None, results_per_page=None, continuation_token=None):
        super(QueuePropertiesPaged, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.prefix = prefix
        self.marker = None
        self.results_per_page = results_per_page
        self.location_mode = None

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
        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.marker = self._response.marker
        self.results_per_page = self._response.max_results
        props_list = [QueueProperties._from_generated(q) for q in self._response.queue_items] # pylint: disable=protected-access
        return self._response.next_marker or None, props_list


class QueuePermissions(object):
    """QueuePermissions class to be used with
    :func:`~azure.storage.queue.queue_client.QueueClient.generate_shared_access_signature`
    method and for the AccessPolicies used with
    :func:`~azure.storage.queue.queue_client.QueueClient.set_queue_access_policy`.

    :ivar QueuePermissions QueuePermissions.READ:
        Read metadata and properties, including message count. Peek at messages.
    :ivar QueuePermissions QueuePermissions.ADD:
        Add messages to the queue.
    :ivar QueuePermissions QueuePermissions.UPDATE:
        Update messages in the queue. Note: Use the Process permission with
        Update so you can first get the message you want to update.
    :ivar QueuePermissions QueuePermissions.PROCESS: Delete entities.
        Get and delete messages from the queue.
    :param bool read:
        Read metadata and properties, including message count. Peek at messages.
    :param bool add:
        Add messages to the queue.
    :param bool update:
        Update messages in the queue. Note: Use the Process permission with
        Update so you can first get the message you want to update.
    :param bool process:
        Get and delete messages from the queue.
    :param str _str:
        A string representing the permissions.
    """

    READ = None # type: QueuePermissions
    ADD = None # type: QueuePermissions
    UPDATE = None # type: QueuePermissions
    PROCESS = None # type: QueuePermissions

    def __init__(self, read=False, add=False, update=False, process=False, _str=None):
        if not _str:
            _str = ''
        self.read = read or ('r' in _str)
        self.add = add or ('a' in _str)
        self.update = update or ('u' in _str)
        self.process = process or ('p' in _str)

    def __or__(self, other):
        return QueuePermissions(_str=str(self) + str(other))

    def __add__(self, other):
        return QueuePermissions(_str=str(self) + str(other))

    def __str__(self):
        return (('r' if self.read else '') +
                ('a' if self.add else '') +
                ('u' if self.update else '') +
                ('p' if self.process else ''))


QueuePermissions.READ = QueuePermissions(read=True)
QueuePermissions.ADD = QueuePermissions(add=True)
QueuePermissions.UPDATE = QueuePermissions(update=True)
QueuePermissions.PROCESS = QueuePermissions(process=True)
