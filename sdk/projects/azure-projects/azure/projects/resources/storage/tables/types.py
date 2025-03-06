from typing import TYPE_CHECKING, TypedDict, Literal, List, Dict, Union
from typing_extensions import Required

from ...._bicep.expressions import Parameter


RESOURCE = "Microsoft.Storage/storageAccounts/tableServices"
VERSION = "2024-01-01"


class TablesCorsRule(TypedDict, total=False):
    allowedHeaders: Required[Union[Parameter[List[str]], List[Union[str, Parameter[str]]]]]
    """A list of headers allowed to be part of the cross-origin request."""
    allowedMethods: Required[Union[Parameter[List[str]], List[Union[Literal['CONNECT', 'DELETE', 'GET', 'HEAD', 'MERGE', 'OPTIONS', 'PATCH', 'POST', 'PUT', 'TRACE'], Parameter[str]]]]]
    """A list of HTTP methods that are allowed to be executed by the origin."""
    allowedOrigins: Required[Union[Parameter[List[str]], List[Union[str, Parameter[str]]]]]
    """A list of origin domains that will be allowed via CORS, or "*" to allow all domains."""
    exposedHeaders: Required[Union[Parameter[List[str]], List[Union[str, Parameter[str]]]]]
    """A list of response headers to expose to CORS clients."""
    maxAgeInSeconds: Required[Union[int, Parameter[int]]]
    """The number of seconds that the client/browser should cache a preflight response."""


class TablesCorsRules(TypedDict, total=False):
    corsRules: Union[Parameter[List[TablesCorsRule]], List[Union[TablesCorsRule, Parameter[TablesCorsRule]]]]
    """The List of CORS rules. You can include up to five CorsRule elements in the request."""


class TableServiceProperties(TypedDict, total=False):
    cors: Union[TablesCorsRules, Parameter[TablesCorsRules]]
    """Specifies CORS rules for the Table service. You can include up to five CorsRule elements in the request. If no CorsRule elements are included in the request body, all CORS rules will be deleted, and CORS will be disabled for the Table service."""


class TableServiceResource(TypedDict, total=False):
    name: Union[Literal['default'], Parameter[str]]
    """The resource name."""
    properties: Union[TableServiceProperties, Parameter[TableServiceProperties]]
    """The properties of a storage account's Table service."""
