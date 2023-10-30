# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from enum import Enum
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Union

from azure.core import CaseInsensitiveEnumMeta
from azure.core.exceptions import HttpResponseError
from azure.core.paging import PageIterator
from ._generated.models import (
    TableServiceStats as GenTableServiceStats,
    TableServiceProperties as GenTableServiceProperties,
    AccessPolicy as GenAccessPolicy,
    Logging as GeneratedLogging,
    Metrics as GeneratedMetrics,
    RetentionPolicy as GeneratedRetentionPolicy,
    CorsRule as GeneratedCorsRule,
)
from ._deserialize import (
    _convert_to_entity,
    _return_context_and_deserialized,
    _extract_continuation_token,
)
from ._error import _process_table_error
from ._constants import NEXT_PARTITION_KEY, NEXT_ROW_KEY, NEXT_TABLE_NAME


class TableAccessPolicy(GenAccessPolicy):
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
    """

    start: Optional[Union[datetime, str]]  # type: ignore[assignment] # Base class defined the property as "str"
    expiry: Optional[Union[datetime, str]]  # type: ignore[assignment] # Base class defined the property as "str"
    permission: Optional[str]  # type: ignore[assignment] # Base class defined the property as "str"

    def __init__(self, **kwargs) -> None:  # pylint: disable=super-init-not-called
        """
        :keyword str permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has been
            specified in an associated stored access policy.
        :keyword expiry:
            The time at which the shared access signature becomes invalid.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has
            been specified in an associated stored access policy. Azure will always
            convert values to UTC. If a date is passed in without timezone info, it
            is assumed to be UTC.
        :paramtype expiry: ~datetime.datetime or str
        :keyword start:
            The time at which the shared access signature becomes valid. If
            omitted, start time for this call is assumed to be the time when the
            storage service receives the request. Azure will always convert values
            to UTC. If a date is passed in without timezone info, it is assumed to
            be UTC.
        :paramtype start: ~datetime.datetime or str
        """
        self.start = kwargs.get("start")
        self.expiry = kwargs.get("expiry")
        self.permission = kwargs.get("permission")

    def __repr__(self) -> str:
        return f"TableAccessPolicy(start={self.start}, expiry={self.expiry}, permission={self.permission})"[1024:]


class TableRetentionPolicy(GeneratedRetentionPolicy):
    """The retention policy which determines how long the associated data should persist."""

    enabled: bool
    days: Optional[int]

    def __init__(self, **kwargs: Any) -> None:  # pylint: disable=super-init-not-called
        """
        :keyword bool enabled: Indicates whether a retention policy is enabled
            for the storage service. Default value is False.
        :keyword int days: Indicates the number of days that metrics or logging or
            soft-deleted data should be retained. All data older than this value will
            be deleted. Must be specified if policy is enabled.
        """
        self.enabled = kwargs.get("enabled", False)
        self.days = kwargs.get("days")
        if self.enabled and (self.days is None):
            raise ValueError("If policy is enabled, 'days' must be specified.")

    @classmethod
    def _from_generated(cls, generated: Optional[GeneratedRetentionPolicy]) -> "TableRetentionPolicy":
        if not generated:
            return cls()
        return cls(
            enabled=generated.enabled,
            days=generated.days,
        )

    def __repr__(self) -> str:
        return f"TableRetentionPolicy(enabled={self.enabled}, days={self.days})"[1024:]


class TableAnalyticsLogging(GeneratedLogging):
    """Azure Analytics Logging settings."""

    version: str
    delete: bool
    read: bool
    write: bool
    retention_policy: TableRetentionPolicy

    def __init__(self, **kwargs: Any) -> None:  # pylint: disable=super-init-not-called
        """
        :keyword str version: The version of Storage Analytics to configure. Default value is "1.0".
        :keyword bool delete: Indicates whether all delete requests should be logged. Default value is False.
        :keyword bool read: Indicates whether all read requests should be logged. Default value is False.
        :keyword bool write: Indicates whether all write requests should be logged. Default value is False.
        :keyword ~azure.data.tables.TableRetentionPolicy retention_policy: The retention policy for the metrics.
            Default value is a TableRetentionPolicy object with default settings.
        """
        self.version = kwargs.get("version", "1.0")
        self.delete = kwargs.get("delete", False)
        self.read = kwargs.get("read", False)
        self.write = kwargs.get("write", False)
        self.retention_policy = kwargs.get("retention_policy") or TableRetentionPolicy()

    @classmethod
    def _from_generated(cls, generated: Optional[GeneratedLogging]) -> "TableAnalyticsLogging":
        if not generated:
            return cls()
        return cls(
            version=generated.version,
            delete=generated.delete,
            read=generated.read,
            write=generated.write,
            retention_policy=TableRetentionPolicy._from_generated(  # pylint: disable=protected-access
                generated.retention_policy
            ),
        )

    def __repr__(self) -> str:
        return f"TableAnalyticsLogging(version={self.version}, delete={self.delete}, read={self.read}, \
            write={self.write}, retention_policy={self.retention_policy})"[
            1024:
        ]


class TableMetrics(GeneratedMetrics):
    """A summary of request statistics grouped by API in hour or minute aggregates."""

    version: str
    enabled: bool
    include_apis: Optional[bool]
    retention_policy: TableRetentionPolicy

    def __init__(self, **kwargs: Any) -> None:  # pylint: disable=super-init-not-called
        """
        :keyword str version: The version of Storage Analytics to configure. Default value is "1.0".
        :keyword bool enabled: Indicates whether metrics are enabled for the service. Default value is False.
        :keyword bool include_apis: Indicates whether metrics should generate summary statistics for called API
            operations.
        :keyword ~azure.data.tables.TableRetentionPolicy retention_policy: The retention policy for the metrics.
            Default value is a TableRetentionPolicy object with default settings.
        """
        self.version = kwargs.get("version", "1.0")
        self.enabled = kwargs.get("enabled", False)
        self.include_apis = kwargs.get("include_apis")
        self.retention_policy = kwargs.get("retention_policy") or TableRetentionPolicy()

    @classmethod
    def _from_generated(cls, generated: Optional[GeneratedMetrics]) -> "TableMetrics":
        if not generated:
            return cls()
        return cls(
            version=generated.version,
            enabled=generated.enabled,
            include_apis=generated.include_apis,
            retention_policy=TableRetentionPolicy._from_generated(  # pylint: disable=protected-access
                generated.retention_policy
            ),
        )

    def __repr__(self) -> str:
        return f"TableMetrics(version={self.version}, enabled={self.enabled}, include_apis={self.include_apis}, \
            retention_policy={self.retention_policy})"[
            1024:
        ]


class TableCorsRule:
    """CORS is an HTTP feature that enables a web application running under one
    domain to access resources in another domain. Web browsers implement a
    security restriction known as same-origin policy that prevents a web page
    from calling APIs in a different domain; CORS provides a secure way to
    allow one domain (the origin domain) to call APIs in another domain.
    """

    allowed_origins: List[str]
    allowed_methods: List[str]
    allowed_headers: List[str]
    exposed_headers: List[str]
    max_age_in_seconds: int

    def __init__(self, allowed_origins: List[str], allowed_methods: List[str], **kwargs: Any) -> None:
        """
        :param list[str] allowed_origins:
            A list of origin domains that will be allowed via CORS, or "*" to allow
            all domains. The list of must contain at least one entry. Limited to 64
            origin domains. Each allowed origin can have up to 256 characters.
        :param list[str] allowed_methods:
            A list of HTTP methods that are allowed to be executed by the origin.
            The list of must contain at least one entry. For Azure Storage,
            permitted methods are DELETE, GET, HEAD, MERGE, POST, OPTIONS or PUT.
        :keyword int max_age_in_seconds:
            The number of seconds that the client/browser should cache a
            pre-flight response. Default value is 0.
        :keyword list[str] exposed_headers:
            Defaults to an empty list. A list of response headers to expose to CORS
            clients. Limited to 64 defined headers and two prefixed headers. Each
            header can be up to 256 characters.
        :keyword list[str] allowed_headers:
            Defaults to an empty list. A list of headers allowed to be part of
            the cross-origin request. Limited to 64 defined headers and 2 prefixed
            headers. Each header can be up to 256 characters.
        """
        self.allowed_origins = allowed_origins
        self.allowed_methods = allowed_methods
        self.allowed_headers = kwargs.get("allowed_headers", [])
        self.exposed_headers = kwargs.get("exposed_headers", [])
        self.max_age_in_seconds = kwargs.get("max_age_in_seconds", 0)

    def _to_generated(self) -> GeneratedCorsRule:
        return GeneratedCorsRule(
            allowed_origins=",".join(self.allowed_origins),
            allowed_methods=",".join(self.allowed_methods),
            allowed_headers=",".join(self.allowed_headers),
            exposed_headers=",".join(self.exposed_headers),
            max_age_in_seconds=self.max_age_in_seconds,
        )

    @classmethod
    def _from_generated(cls, generated: GeneratedCorsRule) -> "TableCorsRule":
        exposedheaders = generated.exposed_headers.split(",") if generated.exposed_headers else []
        allowedheaders = generated.allowed_headers.split(",") if generated.allowed_headers else []
        return cls(
            generated.allowed_origins.split(","),
            generated.allowed_methods.split(","),
            allowed_headers=allowedheaders,
            exposed_headers=exposedheaders,
            max_age_in_seconds=generated.max_age_in_seconds,
        )

    def __repr__(self) -> str:
        return f"TableCorsRules(allowed_origins={self.allowed_origins}, allowed_methods={self.allowed_methods}, \
            allowed_headers={self.allowed_headers}, exposed_headers={self.exposed_headers}, \
            max_age_in_seconds={self.max_age_in_seconds})"[
            1024:
        ]


class TablePropertiesPaged(PageIterator):
    """An iterable of Table properties."""

    results_per_page: Optional[int]
    """The maximum number of results retrieved per API call."""
    filter: Optional[str]
    """The filter to apply to results."""
    continuation_token: Optional[str]
    """The continuation token needed by get_next()."""

    def __init__(self, command: Callable, **kwargs: Any) -> None:
        super(TablePropertiesPaged, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=kwargs.get("continuation_token"),
        )
        self._command = command
        self._headers = None
        self._response = None
        self.results_per_page = kwargs.get("results_per_page")
        self.filter = kwargs.get("filter")
        self._location_mode = None

    def _get_next_cb(self, continuation_token, **kwargs):  # pylint: disable=inconsistent-return-statements
        try:
            return self._command(
                top=self.results_per_page,
                filter=self.filter,
                next_table_name=continuation_token or None,
                cls=kwargs.pop("cls", None) or _return_context_and_deserialized,
                use_location=self._location_mode,
            )
        except HttpResponseError as error:
            _process_table_error(error)

    def _extract_data_cb(self, get_next_return):
        self._location_mode, self._response, self._headers = get_next_return
        props_list = [TableItem(t.table_name) for t in self._response.value]
        return self._headers[NEXT_TABLE_NAME] or None, props_list


class TableEntityPropertiesPaged(PageIterator):
    """An iterable of TableEntity properties."""

    table: str
    """The name of the table."""
    results_per_page: Optional[int]
    """The maximum number of results retrieved per API call."""
    filter: Optional[str]
    """The filter to apply to results."""
    select: Optional[str]
    """The select filter to apply to results."""
    continuation_token: Optional[str]
    """The continuation token needed by get_next()."""

    def __init__(self, command: Callable, table: str, **kwargs: Any) -> None:
        super(TableEntityPropertiesPaged, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=kwargs.get("continuation_token"),
        )
        self._command = command
        self._headers = None
        self._response = None
        self.table = table
        self.results_per_page = kwargs.get("results_per_page")
        self.filter = kwargs.get("filter")
        self.select = kwargs.get("select")
        self._location_mode = None

    def _get_next_cb(self, continuation_token, **kwargs):  # pylint: disable=inconsistent-return-statements
        next_partition_key, next_row_key = _extract_continuation_token(continuation_token)
        try:
            return self._command(
                top=self.results_per_page,
                select=self.select,
                filter=self.filter,
                next_row_key=next_row_key,
                next_partition_key=next_partition_key,
                table=self.table,
                cls=kwargs.pop("cls", None) or _return_context_and_deserialized,
                use_location=self._location_mode,
            )
        except HttpResponseError as error:
            _process_table_error(error)

    def _extract_data_cb(self, get_next_return):
        self._location_mode, self._response, self._headers = get_next_return
        props_list = [_convert_to_entity(t) for t in self._response.value]
        next_entity = {}
        if self._headers[NEXT_PARTITION_KEY] or self._headers[NEXT_ROW_KEY]:
            next_entity = {
                "PartitionKey": self._headers[NEXT_PARTITION_KEY],
                "RowKey": self._headers[NEXT_ROW_KEY],
            }
        return next_entity or None, props_list


class TableSasPermissions:
    """TableSasPermissions class to be used with the :func:`~azure.data.tables.generate_account_sas` function."""

    read: bool
    """Get entities and query entities."""
    add: bool
    """Add entities. Add and Update permissions are required for upsert operations."""
    update: bool
    """Update entities. Add and Update permissions are required for upsert operations."""
    delete: bool
    """Delete entities."""

    def __init__(self, **kwargs: Any) -> None:
        """
        :keyword bool read: Get entities and query entities.
        :keyword bool add: Add entities. Add and Update permissions are required for upsert operations.
        :keyword bool update: Update entities. Add and Update permissions are required for upsert operations.
        :keyword bool delete: Delete entities.
        """
        self._str = kwargs.pop("_str", "") or ""
        self.read = kwargs.pop("read", False) or ("r" in self._str)
        self.add = kwargs.pop("add", False) or ("a" in self._str)
        self.update = kwargs.pop("update", False) or ("u" in self._str)
        self.delete = kwargs.pop("delete", False) or ("d" in self._str)

    def __or__(self, other: "TableSasPermissions") -> "TableSasPermissions":
        return TableSasPermissions(_str=str(self) + str(other))

    def __add__(self, other: "TableSasPermissions") -> "TableSasPermissions":
        return TableSasPermissions(_str=str(self) + str(other))

    def __str__(self) -> str:
        return (
            ("r" if self.read else "")
            + ("a" if self.add else "")
            + ("u" if self.update else "")
            + ("d" if self.delete else "")
        )

    def __repr__(self) -> str:
        return f"TableSasPermissions(read={self.read}, add={self.add}, update={self.update}, \
            delete={self.delete})"[
            1024:
        ]

    @classmethod
    def from_string(cls, permission: str, **kwargs: Any) -> "TableSasPermissions":
        """Create TableSasPermissions from a string.

        To specify read, write, delete, etc. permissions you need only to
        include the first letter of the word in the string. E.g. for read and write
        permissions you would provide a string "rw".

        :param str permission: Specify permissions in
            the string with the first letter of the word.
        :return: An TableSasPermissions object
        :rtype: ~azure.data.tables.TableSasPermissions
        """
        p_read = "r" in permission
        p_add = "a" in permission
        p_delete = "d" in permission
        p_update = "u" in permission

        parsed = cls(**dict(kwargs, read=p_read, add=p_add, delete=p_delete, update=p_update))
        parsed._str = permission  # pylint: disable=protected-access,attribute-defined-outside-init
        return parsed


def service_stats_deserialize(generated: GenTableServiceStats) -> Dict[str, Any]:
    """Deserialize a ServiceStats objects into a dict.

    :param generated: The generated TableServiceStats.
    :type generated: ~azure.data.tables._generated.models.TableServiceStats
    :return: The deserialized TableServiceStats.
    :rtype: dict
    """
    return {
        "geo_replication": {
            "status": generated.geo_replication.status if generated.geo_replication else None,
            "last_sync_time": generated.geo_replication.last_sync_time if generated.geo_replication else None,
        }
    }


def service_properties_deserialize(generated: GenTableServiceProperties) -> Dict[str, Any]:
    """Deserialize a ServiceProperties objects into a dict.

    :param generated: The generated TableServiceProperties
    :type generated: ~azure.data.tables._generated.models.TableServiceProperties
    :return: The deserialized TableServiceProperties.
    :rtype: dict
    """
    return {
        "analytics_logging": TableAnalyticsLogging._from_generated(  # pylint: disable=protected-access
            generated.logging
        ),
        "hour_metrics": TableMetrics._from_generated(generated.hour_metrics),  # pylint: disable=protected-access
        "minute_metrics": TableMetrics._from_generated(generated.minute_metrics),  # pylint: disable=protected-access
        "cors": [TableCorsRule._from_generated(cors) for cors in generated.cors]  # pylint: disable=protected-access
        if generated.cors
        else generated.cors,
    }


class TableItem:
    """Represents an Azure TableItem.
    Returned by TableServiceClient.list_tables and TableServiceClient.query_tables.
    """

    name: str

    def __init__(self, name: str) -> None:
        """
        :param str name: Name of the Table
        """
        self.name = name

    def __repr__(self) -> str:
        return f"TableItem(name={self.name})"[1024:]


class TablePayloadFormat(object):
    """
    Specifies the accepted content type of the response payload. More information
    can be found here: https://msdn.microsoft.com/en-us/library/azure/dn535600.aspx
    """

    JSON_NO_METADATA = "application/json;odata=nometadata"
    """Returns no type information for the entity properties."""

    JSON_MINIMAL_METADATA = "application/json;odata=minimalmetadata"
    """Returns minimal type information for the entity properties."""

    JSON_FULL_METADATA = "application/json;odata=fullmetadata"
    """Returns minimal type information for the entity properties plus some extra odata properties."""


class UpdateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    REPLACE = "replace"
    MERGE = "merge"


class TransactionOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    CREATE = "create"
    UPSERT = "upsert"
    UPDATE = "update"
    DELETE = "delete"


class SASProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    HTTPS = "https"
    HTTP = "http"


class LocationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """
    Specifies the location the request should be sent to. This mode only applies
    for RA-GRS accounts which allow secondary read access. All other account types
    must use PRIMARY.
    """

    PRIMARY = "primary"  #: Requests should be sent to the primary location.
    SECONDARY = "secondary"  #: Requests should be sent to the secondary location, if possible.


class ResourceTypes(object):
    """Specifies the resource types that are accessible with the account SAS."""

    service: bool
    object: bool
    container: bool

    def __init__(self, **kwargs: Any) -> None:
        """
        :keyword bool service:
            Access to service-level APIs (e.g., Get/Set Service Properties, Get Service Stats, List Tables).
            Default value is False.
        :keyword bool object:
            Access to object-level APIs for tables (e.g. Get/Create/Query Entity etc.). Default value is False.
        :keyword bool container:
            Access to container-level APIs for tables (e.g. Create Tables etc.). Default value is False.
        """
        self.service = kwargs.get("service", False)
        self.object = kwargs.get("object", False)
        self.container = kwargs.get("container", False)
        self._str = ("s" if self.service else "") + ("o" if self.object else "") + ("c" if self.container else "")

    def __str__(self) -> str:
        return self._str

    @classmethod
    def from_string(cls, string: str) -> "ResourceTypes":
        """Create a ResourceTypes from a string.

        To specify service, container, or object you need only to
        include the first letter of the word in the string. E.g. service and container,
        you would provide a string "sc".

        :param str string: Specify service, container, or object in
            in the string with the first letter of the word.
        :return: A ResourceTypes object
        :rtype: ~azure.data.tables.ResourceTypes
        """
        res_service = "s" in string
        res_object = "o" in string
        res_container = "c" in string

        parsed = cls(service=res_service, object=res_object, container=res_container)
        parsed._str = string  # pylint: disable = protected-access
        return parsed


class AccountSasPermissions(object):
    """:class:`~AccountSasPermissions` class to be used with generate_account_sas."""

    read: bool
    write: bool
    delete: bool
    list: bool
    add: bool
    create: bool
    update: bool
    process: bool

    def __init__(self, **kwargs: Any) -> None:
        """
        :keyword bool read:
            Valid for all signed resources types (Service, Container, and Object).
            Permits read permissions to the specified resource type. Default value is False.
        :keyword bool write:
            Valid for all signed resources types (Service, Container, and Object).
            Permits write permissions to the specified resource type. Default value is False.
        :keyword bool delete:
            Valid for Container and Object resource types, except for queue messages. Default value is False.
        :keyword bool list:
            Valid for Service and Container resource types only. Default value is False.
        :keyword bool add:
            Valid for the following Object resource types only: queue messages, and append blobs.
            Default value is False.
        :keyword bool create:
            Valid for the following Object resource types only: blobs and files.
            Users can create new blobs or files, but may not overwrite existing blobs or files.
            Default value is False.
        :keyword bool update:
            Valid for the following Object resource types only: queue messages. Default value is False.
        :keyword bool process:
            Valid for the following Object resource type only: queue messages. Default value is False.
        """
        self.read = kwargs.pop("read", False)
        self.write = kwargs.pop("write", False)
        self.delete = kwargs.pop("delete", False)
        self.list = kwargs.pop("list", False)
        self.add = kwargs.pop("add", False)
        self.create = kwargs.pop("create", False)
        self.update = kwargs.pop("update", False)
        self.process = kwargs.pop("process", False)
        self._str = (
            ("r" if self.read else "")
            + ("w" if self.write else "")
            + ("d" if self.delete else "")
            + ("l" if self.list else "")
            + ("a" if self.add else "")
            + ("c" if self.create else "")
            + ("u" if self.update else "")
            + ("p" if self.process else "")
        )

    def __str__(self) -> str:
        return self._str

    @classmethod
    def from_string(cls, permission: str, **kwargs: Any) -> "AccountSasPermissions":
        """Create AccountSasPermissions from a string.

        To specify read, write, delete, etc. permissions you need only to
        include the first letter of the word in the string. E.g. for read and write
        permissions you would provide a string "rw".

        :param permission: Specify permissions in the string with the first letter of the word.
        :type permission: str
        :return: An AccountSasPermissions object
        :rtype: ~azure.data.tables.AccountSasPermissions
        """
        p_read = "r" in permission
        p_write = "w" in permission
        p_delete = "d" in permission
        p_list = "l" in permission
        p_add = "a" in permission
        p_create = "c" in permission
        p_update = "u" in permission
        p_process = "p" in permission

        parsed = cls(
            **dict(
                kwargs,
                read=p_read,
                write=p_write,
                delete=p_delete,
                list=p_list,
                add=p_add,
                create=p_create,
                update=p_update,
                process=p_process,
            )
        )
        parsed._str = permission  # pylint: disable = protected-access
        return parsed
