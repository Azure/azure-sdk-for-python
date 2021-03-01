# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from enum import Enum


def get_enum_value(value):
    if value is None or value in ["None", ""]:
        return None
    try:
        return value.value
    except AttributeError:
        return value


class TableErrorCode(str, Enum):
    # Generic storage values
    account_already_exists = "AccountAlreadyExists"
    account_being_created = "AccountBeingCreated"
    account_is_disabled = "AccountIsDisabled"
    authentication_failed = "AuthenticationFailed"
    authorization_failure = "AuthorizationFailure"
    no_authentication_information = "NoAuthenticationInformation"
    condition_headers_not_supported = "ConditionHeadersNotSupported"
    condition_not_met = "ConditionNotMet"
    empty_metadata_key = "EmptyMetadataKey"
    insufficient_account_permissions = "InsufficientAccountPermissions"
    internal_error = "InternalError"
    invalid_authentication_info = "InvalidAuthenticationInfo"
    invalid_header_value = "InvalidHeaderValue"
    invalid_http_verb = "InvalidHttpVerb"
    invalid_input = "InvalidInput"
    invalid_md5 = "InvalidMd5"
    invalid_metadata = "InvalidMetadata"
    invalid_query_parameter_value = "InvalidQueryParameterValue"
    invalid_range = "InvalidRange"
    invalid_resource_name = "InvalidResourceName"
    invalid_uri = "InvalidUri"
    invalid_xml_document = "InvalidXmlDocument"
    invalid_xml_node_value = "InvalidXmlNodeValue"
    md5_mismatch = "Md5Mismatch"
    metadata_too_large = "MetadataTooLarge"
    missing_content_length_header = "MissingContentLengthHeader"
    missing_required_query_parameter = "MissingRequiredQueryParameter"
    missing_required_header = "MissingRequiredHeader"
    missing_required_xml_node = "MissingRequiredXmlNode"
    multiple_condition_headers_not_supported = "MultipleConditionHeadersNotSupported"
    operation_timed_out = "OperationTimedOut"
    out_of_range_input = "OutOfRangeInput"
    out_of_range_query_parameter_value = "OutOfRangeQueryParameterValue"
    request_body_too_large = "RequestBodyTooLarge"
    resource_type_mismatch = "ResourceTypeMismatch"
    request_url_failed_to_parse = "RequestUrlFailedToParse"
    resource_already_exists = "ResourceAlreadyExists"
    resource_not_found = "ResourceNotFound"
    server_busy = "ServerBusy"
    unsupported_header = "UnsupportedHeader"
    unsupported_xml_node = "UnsupportedXmlNode"
    unsupported_query_parameter = "UnsupportedQueryParameter"
    unsupported_http_verb = "UnsupportedHttpVerb"

    # table error codes
    duplicate_properties_specified = "DuplicatePropertiesSpecified"
    entity_not_found = "EntityNotFound"
    entity_already_exists = "EntityAlreadyExists"
    entity_too_large = "EntityTooLarge"
    host_information_not_present = "HostInformationNotPresent"
    invalid_duplicate_row = "InvalidDuplicateRow"
    invalid_value_type = "InvalidValueType"
    json_format_not_supported = "JsonFormatNotSupported"
    method_not_allowed = "MethodNotAllowed"
    not_implemented = "NotImplemented"
    properties_need_value = "PropertiesNeedValue"
    property_name_invalid = "PropertyNameInvalid"
    property_name_too_long = "PropertyNameTooLong"
    property_value_too_large = "PropertyValueTooLarge"
    table_already_exists = "TableAlreadyExists"
    table_being_deleted = "TableBeingDeleted"
    table_not_found = "TableNotFound"
    too_many_properties = "TooManyProperties"
    update_condition_not_satisfied = "UpdateConditionNotSatisfied"
    x_method_incorrect_count = "XMethodIncorrectCount"
    x_method_incorrect_value = "XMethodIncorrectValue"
    x_method_not_using_post = "XMethodNotUsingPost"


class DictMixin(object):

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, key):
        self.__dict__[key] = None

    def __eq__(self, other):
        """Compare objects by comparing all attributes."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        """Compare objects by comparing all attributes."""
        return not self.__eq__(other)

    def __str__(self):
        return str({k: v for k, v in self.__dict__.items() if not k.startswith('_')})

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return [k for k in self.__dict__ if not k.startswith('_')]

    def values(self):
        return [v for k, v in self.__dict__.items() if not k.startswith('_')]

    def items(self):
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith('_')]

    def get(self, key, default=None):
        if key in self.__dict__:
            return self.__dict__[key]
        return default


class LocationMode(object):
    """
    Specifies the location the request should be sent to. This mode only applies
    for RA-GRS accounts which allow secondary read access. All other account types
    must use PRIMARY.
    """

    PRIMARY = 'primary'  #: Requests should be sent to the primary location.
    SECONDARY = 'secondary'  #: Requests should be sent to the secondary location, if possible.


class ResourceTypes(object):
    """
    Specifies the resource types that are accessible with the account SAS.

    :param bool service:
        Access to service-level APIs (e.g., Get/Set Service Properties,
        Get Service Stats, List Containers/Queues/Shares)
    :param bool object:
        Access to object-level APIs for blobs, queue messages, and
        files(e.g. Put Blob, Query Entity, Get Messages, Create File, etc.)
    """

    def __init__(self, service=False, object=False):  # pylint: disable=redefined-builtin
        self.service = service
        self.object = object
        self._str = (('s' if self.service else '') +
                     ('o' if self.object else ''))

    def __str__(self):
        return self._str

    @classmethod
    def from_string(cls, string):
        """Create a ResourceTypes from a string.

        To specify service, container, or object you need only to
        include the first letter of the word in the string. E.g. service and container,
        you would provide a string "sc".

        :param str string: Specify service, container, or object in
            in the string with the first letter of the word.
        :return: A ResourceTypes object
        :rtype: ~azure.table.ResourceTypes
        """
        res_service = 's' in string
        res_object = 'o' in string

        parsed = cls(res_service, res_object)
        parsed._str = string  # pylint: disable = protected-access
        return parsed


class AccountSasPermissions(object):
    """
    :class:`~ResourceTypes` class to be used with generate_account_sas
    function and for the AccessPolicies used with set_*_acl. There are two types of
    SAS which may be used to grant resource access. One is to grant access to a
    specific resource (resource-specific). Another is to grant access to the
    entire service for a specific account and allow certain operations based on
    perms found here.

    :ivar bool read:
        Valid for all signed resources types (Service, Container, and Object).
        Permits read permissions to the specified resource type.
    :ivar bool write:
        Valid for all signed resources types (Service, Container, and Object).
        Permits write permissions to the specified resource type.
    :ivar bool delete:
        Valid for Container and Object resource types, except for queue messages.
    :ivar bool list:
        Valid for Service and Container resource types only.
    :ivar bool add:
        Valid for the following Object resource types only: queue messages, and append blobs.
    :ivar bool create:
        Valid for the following Object resource types only: blobs and files.
        Users can create new blobs or files, but may not overwrite existing
        blobs or files.
    :ivar bool update:
        Valid for the following Object resource types only: queue messages.
    :ivar bool process:
        Valid for the following Object resource type only: queue messages.
    """

    def __init__(self, **kwargs):  # pylint: disable=redefined-builtin
        self.read = kwargs.pop('read', None)
        self.write = kwargs.pop('write', None)
        self.delete = kwargs.pop('delete', None)
        self.list = kwargs.pop('list', None)
        self.add = kwargs.pop('add', None)
        self.create = kwargs.pop('create', None)
        self.update = kwargs.pop('update', None)
        self.process = kwargs.pop('process', None)
        self._str = (('r' if self.read else '') +
                     ('w' if self.write else '') +
                     ('d' if self.delete else '') +
                     ('l' if self.list else '') +
                     ('a' if self.add else '') +
                     ('c' if self.create else '') +
                     ('u' if self.update else '') +
                     ('p' if self.process else ''))

    def __str__(self):
        return self._str

    @classmethod
    def from_string(cls, permission, **kwargs):  # pylint:disable=W0613
        """Create AccountSasPermissions from a string.

        To specify read, write, delete, etc. permissions you need only to
        include the first letter of the word in the string. E.g. for read and write
        permissions you would provide a string "rw".

        :param str permission: Specify permissions in
            the string with the first letter of the word.
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: A AccountSasPermissions object
        :rtype: ~azure.table.AccountSasPermissions
        """
        p_read = 'r' in permission
        p_write = 'w' in permission
        p_delete = 'd' in permission
        p_list = 'l' in permission
        p_add = 'a' in permission
        p_create = 'c' in permission
        p_update = 'u' in permission
        p_process = 'p' in permission

        parsed = cls(
            **dict(kwargs, read=p_read, write=p_write, delete=p_delete, list=p_list, add=p_add, create=p_create,
                   update=p_update, process=p_process))
        parsed._str = permission  # pylint: disable = protected-access
        return parsed


class Services(object):
    """Specifies the services accessible with the account SAS.

    :param bool blob:
        Access for the `~azure.storage.blob.BlobServiceClient`
    :param bool queue:
        Access for the `~azure.table.QueueServiceClient`
    :param bool fileshare:
        Access for the `~azure.storage.fileshare.ShareServiceClient`
    """

    def __init__(self, blob=False, queue=False, fileshare=False):
        self.blob = blob
        self.queue = queue
        self.fileshare = fileshare
        self._str = (('b' if self.blob else '') +
                     ('q' if self.queue else '') +
                     ('f' if self.fileshare else ''))

    def __str__(self):
        return self._str

    @classmethod
    def from_string(cls, string):
        """Create Services from a string.

        To specify blob, queue, or file you need only to
        include the first letter of the word in the string. E.g. for blob and queue
        you would provide a string "bq".

        :param str string: Specify blob, queue, or file in
            in the string with the first letter of the word.
        :return: A Services object
        :rtype: ~azure.table.Services
        """
        res_blob = 'b' in string
        res_queue = 'q' in string
        res_file = 'f' in string

        parsed = cls(res_blob, res_queue, res_file)
        parsed._str = string  # pylint: disable = protected-access
        return parsed


class UserDelegationKey(object):
    """
    Represents a user delegation key, provided to the user by Azure Storage
    based on their Azure Active Directory access token.

    The fields are saved as simple strings since the user does not have to interact with this object;
    to generate an identify SAS, the user can simply pass it to the right API.

    :ivar str signed_oid:
        Object ID of this token.
    :ivar str signed_tid:
        Tenant ID of the tenant that issued this token.
    :ivar str signed_start:
        The datetime this token becomes valid.
    :ivar str signed_expiry:
        The datetime this token expires.
    :ivar str signed_service:
        What service this key is valid for.
    :ivar str signed_version:
        The version identifier of the REST service that created this token.
    :ivar str value:
        The user delegation key.
    """

    def __init__(self):
        self.signed_oid = None
        self.signed_tid = None
        self.signed_start = None
        self.signed_expiry = None
        self.signed_service = None
        self.signed_version = None
        self.value = None
