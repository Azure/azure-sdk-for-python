# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Base functions in the Azure Cosmos database service.
"""

import base64
from email.utils import formatdate
import json
import uuid
import re
import binascii
from typing import Dict, Any, List, Mapping, Optional, Sequence, Union, Tuple, TYPE_CHECKING

from urllib.parse import quote as urllib_quote
from urllib.parse import urlsplit
from azure.core import MatchConditions

from . import documents
from . import http_constants
from . import _runtime_constants
from .auth import _get_authorization_header
from .offer import ThroughputProperties
from .partition_key import _Empty, _Undefined

if TYPE_CHECKING:
    from ._cosmos_client_connection import CosmosClientConnection
    from .aio._cosmos_client_connection_async import CosmosClientConnection as AsyncClientConnection


_COMMON_OPTIONS = {
    'initial_headers': 'initialHeaders',
    'pre_trigger_include': 'preTriggerInclude',
    'post_trigger_include': 'postTriggerInclude',
    'access_condition': 'accessCondition',
    'session_token': 'sessionToken',
    'resource_token_expiry_seconds': 'resourceTokenExpirySeconds',
    'offer_enable_ru_per_minute_throughput': 'offerEnableRUPerMinuteThroughput',
    'disable_ru_per_minute_usage': 'disableRUPerMinuteUsage',
    'continuation': 'continuation',
    'content_type': 'contentType',
    'is_query_plan_request': 'isQueryPlanRequest',
    'supported_query_features': 'supportedQueryFeatures',
    'query_version': 'queryVersion',
    'priority': 'priorityLevel',
    'no_response': 'responsePayloadOnWriteDisabled'
}

# Cosmos resource ID validation regex breakdown:
# ^ Match start of string.
# [^/\#?] Match any character that is not /\#?\n\r\t.
# $ End of string
_VALID_COSMOS_RESOURCE = re.compile(r"^[^/\\#?\t\r\n]*$")


def _get_match_headers(kwargs: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    if_match = kwargs.pop('if_match', None)
    if_none_match = kwargs.pop('if_none_match', None)
    match_condition = kwargs.pop('match_condition', None)
    if match_condition == MatchConditions.IfNotModified:
        if_match = kwargs.pop('etag', None)
        if not if_match:
            raise ValueError("'match_condition' specified without 'etag'.")
    elif match_condition == MatchConditions.IfPresent:
        if_match = '*'
    elif match_condition == MatchConditions.IfModified:
        if_none_match = kwargs.pop('etag', None)
        if not if_none_match:
            raise ValueError("'match_condition' specified without 'etag'.")
    elif match_condition == MatchConditions.IfMissing:
        if_none_match = '*'
    elif match_condition is None:
        if 'etag' in kwargs:
            raise ValueError("'etag' specified without 'match_condition'.")
    else:
        raise TypeError("Invalid match condition: {}".format(match_condition))
    return if_match, if_none_match


def build_options(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    options = kwargs.pop('request_options', kwargs.pop('feed_options', {}))
    for key, value in _COMMON_OPTIONS.items():
        if key in kwargs:
            options[value] = kwargs.pop(key)
    if_match, if_none_match = _get_match_headers(kwargs)
    if if_match:
        options['accessCondition'] = {'type': 'IfMatch', 'condition': if_match}
    if if_none_match:
        options['accessCondition'] = {'type': 'IfNoneMatch', 'condition': if_none_match}
    return options


def GetHeaders(  # pylint: disable=too-many-statements,too-many-branches
        cosmos_client_connection: Union["CosmosClientConnection", "AsyncClientConnection"],
        default_headers: Mapping[str, Any],
        verb: str,
        path: str,
        resource_id: Optional[str],
        resource_type: str,
        options: Mapping[str, Any],
        partition_key_range_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Gets HTTP request headers.

    :param _cosmos_client_connection.CosmosClientConnection cosmos_client_connection:
    :param dict default_headers:
    :param str verb:
    :param str path:
    :param str resource_id:
    :param str resource_type:
    :param dict options:
    :param str partition_key_range_id:
    :return: The HTTP request headers.
    :rtype: dict
    """
    headers = dict(default_headers)
    options = options or {}

    if cosmos_client_connection.UseMultipleWriteLocations:
        headers[http_constants.HttpHeaders.AllowTentativeWrites] = "true"

    pre_trigger_include = options.get("preTriggerInclude")
    if pre_trigger_include:
        headers[http_constants.HttpHeaders.PreTriggerInclude] = (
            pre_trigger_include if isinstance(pre_trigger_include, str) else (",").join(pre_trigger_include)
        )

    post_trigger_include = options.get("postTriggerInclude")
    if post_trigger_include:
        headers[http_constants.HttpHeaders.PostTriggerInclude] = (
            post_trigger_include if isinstance(post_trigger_include, str) else (",").join(post_trigger_include)
        )

    if options.get("maxItemCount"):
        headers[http_constants.HttpHeaders.PageSize] = options["maxItemCount"]

    access_condition = options.get("accessCondition")
    if access_condition:
        if access_condition["type"] == "IfMatch":
            headers[http_constants.HttpHeaders.IfMatch] = access_condition["condition"]
        else:
            headers[http_constants.HttpHeaders.IfNoneMatch] = access_condition["condition"]

    if options.get("indexingDirective"):
        headers[http_constants.HttpHeaders.IndexingDirective] = options["indexingDirective"]

    consistency_level = None

    # get default client consistency level
    default_client_consistency_level = headers.get(http_constants.HttpHeaders.ConsistencyLevel)

    # set consistency level. check if set via options, this will override the default
    if options.get("consistencyLevel"):
        consistency_level = options["consistencyLevel"]
        headers[http_constants.HttpHeaders.ConsistencyLevel] = consistency_level
    elif default_client_consistency_level is not None:
        consistency_level = default_client_consistency_level
        headers[http_constants.HttpHeaders.ConsistencyLevel] = consistency_level

    # figure out if consistency level for this request is session
    is_session_consistency = consistency_level == documents.ConsistencyLevel.Session

    # set session token if required
    if is_session_consistency is True and not IsMasterResource(resource_type):
        # if there is a token set via option, then use it to override default
        if options.get("sessionToken"):
            headers[http_constants.HttpHeaders.SessionToken] = options["sessionToken"]
        else:
            # check if the client's default consistency is session (and request consistency level is same),
            # then update from session container
            if default_client_consistency_level == documents.ConsistencyLevel.Session and \
                    cosmos_client_connection.session:
                # populate session token from the client's session container
                headers[http_constants.HttpHeaders.SessionToken] = cosmos_client_connection.session.get_session_token(
                    path
                )

    if options.get("enableScanInQuery"):
        headers[http_constants.HttpHeaders.EnableScanInQuery] = options["enableScanInQuery"]

    if options.get("resourceTokenExpirySeconds"):
        headers[http_constants.HttpHeaders.ResourceTokenExpiry] = options["resourceTokenExpirySeconds"]

    if options.get("offerType"):
        headers[http_constants.HttpHeaders.OfferType] = options["offerType"]

    if options.get("offerThroughput"):
        headers[http_constants.HttpHeaders.OfferThroughput] = options["offerThroughput"]

    if options.get("contentType"):
        headers[http_constants.HttpHeaders.ContentType] = options['contentType']

    if options.get("isQueryPlanRequest"):
        headers[http_constants.HttpHeaders.IsQueryPlanRequest] = options['isQueryPlanRequest']

    if options.get("supportedQueryFeatures"):
        headers[http_constants.HttpHeaders.SupportedQueryFeatures] = options['supportedQueryFeatures']

    if options.get("queryVersion"):
        headers[http_constants.HttpHeaders.QueryVersion] = options['queryVersion']

    if "partitionKey" in options:
        # if partitionKey value is Undefined, serialize it as [{}] to be consistent with other SDKs.
        if isinstance(options["partitionKey"], _Undefined):
            headers[http_constants.HttpHeaders.PartitionKey] = [{}]
        # If partitionKey value is Empty, serialize it as [], which is the equivalent sent for migrated collections
        elif isinstance(options["partitionKey"], _Empty):
            headers[http_constants.HttpHeaders.PartitionKey] = []
        # else serialize using json dumps method which apart from regular values will serialize None into null
        else:
            # single partitioning uses a string and needs to be turned into a list
            is_sequence_not_string = (isinstance(options["partitionKey"], Sequence) and
                                      not isinstance(options["partitionKey"], str))

            if is_sequence_not_string and options["partitionKey"]:
                pk_val = json.dumps(list(options["partitionKey"]), separators=(',', ':'))
            else:
                pk_val = json.dumps([options["partitionKey"]])
            headers[http_constants.HttpHeaders.PartitionKey] = pk_val

    if options.get("enableCrossPartitionQuery"):
        headers[http_constants.HttpHeaders.EnableCrossPartitionQuery] = options["enableCrossPartitionQuery"]

    if options.get("populateQueryMetrics"):
        headers[http_constants.HttpHeaders.PopulateQueryMetrics] = options["populateQueryMetrics"]

    if options.get("populateIndexMetrics"):
        headers[http_constants.HttpHeaders.PopulateIndexMetrics] = options["populateIndexMetrics"]

    if options.get("responseContinuationTokenLimitInKb"):
        headers[http_constants.HttpHeaders.ResponseContinuationTokenLimitInKb] = options[
            "responseContinuationTokenLimitInKb"]

    if options.get("priorityLevel"):
        headers[http_constants.HttpHeaders.PriorityLevel] = options["priorityLevel"]

    # formatdate guarantees RFC 1123 date format regardless of current locale
    headers[http_constants.HttpHeaders.XDate] = formatdate(timeval=None, localtime=False, usegmt=True)

    if cosmos_client_connection.master_key or cosmos_client_connection.resource_tokens:
        resource_type = _internal_resourcetype(resource_type)
        authorization = _get_authorization_header(
            cosmos_client_connection, verb, path, resource_id, IsNameBased(resource_id), resource_type, headers
        )
        # urllib.quote throws when the input parameter is None
        if authorization:
            # -_.!~*'() are valid characters in url, and shouldn't be quoted.
            authorization = urllib_quote(authorization, "-_.!~*'()")
        headers[http_constants.HttpHeaders.Authorization] = authorization

    if verb in ("post", "put"):
        if not headers.get(http_constants.HttpHeaders.ContentType):
            headers[http_constants.HttpHeaders.ContentType] = _runtime_constants.MediaTypes.Json

    if not headers.get(http_constants.HttpHeaders.Accept):
        headers[http_constants.HttpHeaders.Accept] = _runtime_constants.MediaTypes.Json

    if partition_key_range_id is not None:
        headers[http_constants.HttpHeaders.PartitionKeyRangeID] = partition_key_range_id

    if options.get("enableScriptLogging"):
        headers[http_constants.HttpHeaders.EnableScriptLogging] = options["enableScriptLogging"]

    if options.get("offerEnableRUPerMinuteThroughput"):
        headers[http_constants.HttpHeaders.OfferIsRUPerMinuteThroughputEnabled] = options[
            "offerEnableRUPerMinuteThroughput"
        ]

    if options.get("disableRUPerMinuteUsage"):
        headers[http_constants.HttpHeaders.DisableRUPerMinuteUsage] = options["disableRUPerMinuteUsage"]

    if options.get("continuation"):
        headers[http_constants.HttpHeaders.Continuation] = options["continuation"]

    if options.get("populatePartitionKeyRangeStatistics"):
        headers[http_constants.HttpHeaders.PopulatePartitionKeyRangeStatistics] = options[
            "populatePartitionKeyRangeStatistics"
        ]

    if options.get("populateQuotaInfo"):
        headers[http_constants.HttpHeaders.PopulateQuotaInfo] = options["populateQuotaInfo"]

    if options.get("maxIntegratedCacheStaleness"):
        headers[http_constants.HttpHeaders.DedicatedGatewayCacheStaleness] = options["maxIntegratedCacheStaleness"]

    if options.get("autoUpgradePolicy"):
        headers[http_constants.HttpHeaders.AutoscaleSettings] = options["autoUpgradePolicy"]

    if options.get("correlatedActivityId"):
        headers[http_constants.HttpHeaders.CorrelatedActivityId] = options["correlatedActivityId"]

    if resource_type == "docs" and verb != "get":
        if "responsePayloadOnWriteDisabled" in options:
            responsePayloadOnWriteDisabled = options["responsePayloadOnWriteDisabled"]
        else:
            responsePayloadOnWriteDisabled = cosmos_client_connection.connection_policy.ResponsePayloadOnWriteDisabled

        if responsePayloadOnWriteDisabled:
            headers[http_constants.HttpHeaders.Prefer] = "return=minimal"

    # If it is an operation at the container level, verify the rid of the container to see if the cache needs to be
    # refreshed.
    if resource_type != 'dbs' and options.get("containerRID"):
        headers[http_constants.HttpHeaders.IntendedCollectionRID] = options["containerRID"]

    return headers


def GetResourceIdOrFullNameFromLink(resource_link: str) -> Optional[str]:
    """Gets resource id or full name from resource link.

    :param str resource_link:
    :return: The resource id or full name from the resource link.
    :rtype: str
    """
    # For named based, the resource link is the full name
    if IsNameBased(resource_link):
        return TrimBeginningAndEndingSlashes(resource_link)

    # Padding the resource link with leading and trailing slashes if not already
    if resource_link[-1] != "/":
        resource_link = resource_link + "/"

    if resource_link[0] != "/":
        resource_link = "/" + resource_link

    # The path will be in the form of
    # /[resourceType]/[resourceId]/ .... /[resourceType]/[resourceId]/ or
    # /[resourceType]/[resourceId]/ .... /[resourceType]/
    # The result of split will be in the form of
    # ["", [resourceType], [resourceId] ... ,[resourceType], [resourceId], ""]
    # In the first case, to extract the resourceId it will the element
    # before last ( at length -2 ) and the the type will before it
    # ( at length -3 )
    # In the second case, to extract the resource type it will the element
    # before last ( at length -2 )
    path_parts = resource_link.split("/")
    if len(path_parts) % 2 == 0:
        # request in form
        # /[resourceType]/[resourceId]/ .... /[resourceType]/[resourceId]/.
        return str(path_parts[-2])
    return None


def GenerateGuidId() -> str:
    """Gets a random GUID.

    Note that here we use python's UUID generation library. Basically UUID
    is the same as GUID when represented as a string.

    :return:
        The generated random GUID.
    :rtype: str
    """
    return str(uuid.uuid4())


def GetPathFromLink(resource_link: str, resource_type: str = "") -> str:
    """Gets path from resource link with optional resource type

    :param str resource_link:
    :param str resource_type:
    :return: Path from resource link with resource type appended (if provided).
    :rtype: str
    """
    resource_link = TrimBeginningAndEndingSlashes(resource_link)

    if IsNameBased(resource_link):
        # Replace special characters in string using the %xx escape. For example,
        # space(' ') would be replaced by %20 This function is intended for quoting
        # the path section of the URL and excludes '/' to be quoted as that's the
        # default safe char
        resource_link = urllib_quote(resource_link)

    # Padding leading and trailing slashes to the path returned both for name based and resource id based links
    if resource_type:
        return "/" + resource_link + "/" + resource_type + "/"
    return "/" + resource_link + "/"


def IsNameBased(link: Optional[str]) -> bool:
    """Finds whether the link is name based or not

    :param str link:

    :return:
        True if link is name-based; otherwise, False.
    :rtype: boolean
    """
    if not link:
        return False

    # trimming the leading "/"
    if link.startswith("/") and len(link) > 1:
        link = link[1:]

    # Splitting the link(separated by "/") into parts
    parts = link.split("/")

    # First part should be "dbs"
    if not (parts and parts[0].lower() == "dbs"):
        return False

    # The second part is the database id(ResourceID or Name) and cannot be empty
    if len(parts) < 2 or not parts[1]:
        return False

    # Either ResourceID or database name
    databaseID = parts[1]

    # Length of databaseID(in case of ResourceID) is always 8
    if len(databaseID) != 8:
        return True

    return not IsValidBase64String(str(databaseID))


def IsMasterResource(resourceType: str) -> bool:
    return resourceType in (
        http_constants.ResourceType.Offer,
        http_constants.ResourceType.Database,
        http_constants.ResourceType.User,
        http_constants.ResourceType.Permission,
        http_constants.ResourceType.Topology,
        http_constants.ResourceType.DatabaseAccount,
        http_constants.ResourceType.PartitionKeyRange,
        http_constants.ResourceType.Collection,
    )


def IsDatabaseLink(link: str) -> bool:
    """Finds whether the link is a database Self Link or a database ID based link

    :param str link: Link to analyze
    :return: True or False.
    :rtype: boolean
    """
    if not link:
        return False

    # trimming the leading and trailing "/" from the input string
    link = TrimBeginningAndEndingSlashes(link)

    # Splitting the link(separated by "/") into parts
    parts = link.split("/")

    if len(parts) != 2:
        return False

    # First part should be "dbs"
    if not parts[0] or not parts[0].lower() == "dbs":
        return False

    # The second part is the database id(ResourceID or Name) and cannot be empty
    if not parts[1]:
        return False

    return True


def IsItemContainerLink(link: str) -> bool:  # pylint: disable=too-many-return-statements
    """Finds whether the link is a document colllection Self Link or a document colllection ID based link

    :param str link: Link to analyze
    :return: True or False.
    :rtype: boolean
    """
    if not link:
        return False

    # trimming the leading and trailing "/" from the input string
    link = TrimBeginningAndEndingSlashes(link)

    # Splitting the link(separated by "/") into parts
    parts = link.split("/")

    if len(parts) != 4:
        return False

    # First part should be "dbs"
    if not parts[0] or not parts[0].lower() == "dbs":
        return False

    # Third part should be "colls"
    if not parts[2] or not parts[2].lower() == "colls":
        return False

    # The second part is the database id(ResourceID or Name) and cannot be empty
    if not parts[1]:
        return False

    # The fourth part is the document collection id(ResourceID or Name) and cannot be empty
    if not parts[3]:
        return False

    return True


def GetItemContainerInfo(self_link: str, alt_content_path: str, resource_id: str) -> Tuple[str, str]:
    """Given the self link and alt_content_path from the response header and
    result extract the collection name and collection id.

    Every response header has an alt-content-path that is the owner's path in
    ASCII. For document create / update requests, this can be used to get the
    collection name, but for collection create response, we can't use it.

    :param str self_link:
        Self link of the resource, as obtained from response result.
    :param str alt_content_path:
        Owner path of the resource, as obtained from response header.
    :param str resource_id:
        'id' as returned from the response result. This is only used if it is
        deduced that the request was to create a collection.
    :return: tuple of (collection rid, collection name)
    :rtype: tuple
    """

    self_link = TrimBeginningAndEndingSlashes(self_link) + "/"

    index = IndexOfNth(self_link, "/", 4)

    if index != -1:
        collection_id = self_link[0:index]

        if "colls" in self_link:
            # this is a collection request
            index_second_slash = IndexOfNth(alt_content_path, "/", 2)
            if index_second_slash == -1:
                collection_name = alt_content_path + "/colls/" + urllib_quote(resource_id)
                return collection_id, collection_name
            collection_name = alt_content_path
            return collection_id, collection_name
        raise ValueError(
            "Response Not from Server Partition, self_link: {0}, alt_content_path: {1}, id: {2}".format(
                self_link, alt_content_path, resource_id
            )
        )

    raise ValueError("Unable to parse document collection link from " + self_link)


def GetItemContainerLink(link: str) -> str:
    """Gets the document collection link.

    :param str link: Resource link
    :return: Document collection link.
    :rtype: str
    """
    link = TrimBeginningAndEndingSlashes(link) + "/"

    index = IndexOfNth(link, "/", 4)

    if index != -1:
        return link[0:index]
    raise ValueError("Unable to parse document collection link from " + link)


def IndexOfNth(s: str, value: str, n: int) -> int:
    """Gets the index of Nth occurrence of a given character in a string.

    :param str s: Input string
    :param str value: Input char to be searched.
    :param int n: Nth occurrence of char to be searched.
    :return: Index of the Nth occurrence in the string.
    :rtype: int
    """
    remaining = n
    for i, elt in enumerate(s):
        if elt == value:
            remaining -= 1
            if remaining == 0:
                return i
    return -1


def IsValidBase64String(string_to_validate: str) -> bool:
    """Verifies if a string is a valid Base64 encoded string, after
    replacing '-' with '/'

    :param string string_to_validate: String to validate.
    :return: Whether given string is a valid base64 string or not.
    :rtype: str
    """
    # '-' is not supported char for decoding in Python(same as C# and Java) which has
    # similar logic while parsing ResourceID generated by backend
    try:
        buffer = base64.standard_b64decode(string_to_validate.replace("-", "/"))
        if len(buffer) != 4:
            return False
    except Exception as e:  # pylint: disable=broad-except
        if isinstance(e, binascii.Error):
            return False
        raise e
    return True


def TrimBeginningAndEndingSlashes(path: str) -> str:
    """Trims beginning and ending slashes

    :param str path:

    :return:
        Path with beginning and ending slashes trimmed.
    :rtype: str
    """
    if path.startswith("/"):
        # Returns substring starting from index 1 to end of the string
        path = path[1:]

    if path.endswith("/"):
        # Returns substring starting from beginning to last but one char in the string
        path = path[:-1]

    return path


# Parses the paths into a list of token each representing a property
def ParsePaths(paths: List[str]) -> List[str]:
    segmentSeparator = "/"
    tokens = []
    for path in paths:
        currentIndex = 0

        while currentIndex < len(path):
            if path[currentIndex] != segmentSeparator:
                raise ValueError(f"Invalid path character at index {currentIndex}")

            currentIndex += 1
            if currentIndex == len(path):
                break

            # " and ' are treated specially in the sense that they can have the / (segment separator)
            # between them which is considered part of the token
            if path[currentIndex] == '"' or path[currentIndex] == "'":
                quote = path[currentIndex]
                newIndex = currentIndex + 1

                while True:
                    newIndex = path.find(quote, newIndex)
                    if newIndex == -1:
                        raise ValueError(f"Invalid path character at index {currentIndex}")

                    # check if the quote itself is escaped by a preceding \ in which case it's part of the token
                    if path[newIndex - 1] != "\\":
                        break
                    newIndex += 1

                # This will extract the token excluding the quote chars
                token = path[currentIndex + 1: newIndex]
                tokens.append(token)
                currentIndex = newIndex + 1
            else:
                newIndex = path.find(segmentSeparator, currentIndex)
                token = None
                if newIndex == -1:
                    # This will extract the token from currentIndex to end of the string
                    token = path[currentIndex:]
                    currentIndex = len(path)
                else:
                    # This will extract the token from currentIndex to the char before the segmentSeparator
                    token = path[currentIndex:newIndex]
                    currentIndex = newIndex

                token = token.strip()
                tokens.append(token)

    return tokens


def create_scope_from_url(url: str) -> str:
    parsed_url = urlsplit(url)
    if not parsed_url.scheme or not parsed_url.hostname:
        raise ValueError(f"Invalid URL scheme or hostname: {parsed_url!r}")
    return parsed_url.scheme + "://" + parsed_url.hostname + "/.default"


def validate_cache_staleness_value(max_integrated_cache_staleness: Any) -> None:
    int(max_integrated_cache_staleness)  # Will throw error if data type cant be converted to int
    if max_integrated_cache_staleness < 0:
        raise ValueError("Parameter 'max_integrated_cache_staleness_in_ms' can only be an "
                         "integer greater than or equal to zero")


def _validate_resource(resource: Mapping[str, Any]) -> None:
    id_: Optional[str] = resource.get("id")
    if id_:
        try:
            if _VALID_COSMOS_RESOURCE.match(id_) is None:
                raise ValueError("Id contains illegal chars.")
            if id_[-1] in [" ", "\n"]:
                raise ValueError("Id ends with a space or newline.")
        except TypeError as e:
            raise TypeError("Id type must be a string.") from e


def _stringify_auto_scale(offer: ThroughputProperties) -> str:
    auto_scale_params: Optional[Dict[str, Union[None, int, Dict[str, Any]]]] = None
    max_throughput = offer.auto_scale_max_throughput
    increment_percent = offer.auto_scale_increment_percent
    auto_scale_params = {"maxThroughput": max_throughput}
    if increment_percent is not None:
        auto_scale_params["autoUpgradePolicy"] = {"throughputPolicy": {"incrementPercent": increment_percent}}
    auto_scale_settings = json.dumps(auto_scale_params)
    return auto_scale_settings


def _set_throughput_options(offer: Optional[Union[int, ThroughputProperties]], request_options: Dict[str, Any]) -> None:
    if isinstance(offer, int):
        request_options["offerThroughput"] = offer
    elif offer is not None:
        try:
            max_throughput = offer.auto_scale_max_throughput
            increment_percent = offer.auto_scale_increment_percent

            if max_throughput is not None:
                request_options['autoUpgradePolicy'] = _stringify_auto_scale(offer=offer)
            elif increment_percent:
                raise ValueError("auto_scale_max_throughput must be supplied in "
                                 "conjunction with auto_scale_increment_percent")
            if offer.offer_throughput:
                request_options["offerThroughput"] = offer.offer_throughput
        except AttributeError as e:
            raise TypeError("offer_throughput must be int or an instance of ThroughputProperties") from e


def _deserialize_throughput(throughput: List[Dict[str, Dict[str, Any]]]) -> ThroughputProperties:
    properties = throughput[0]
    offer_autopilot: Optional[Dict[str, Any]] = properties['content'].get('offerAutopilotSettings')
    if offer_autopilot and 'autoUpgradePolicy' in offer_autopilot:
        return ThroughputProperties(
            properties=properties,
            auto_scale_max_throughput=offer_autopilot['maxThroughput'],
            auto_scale_increment_percent=offer_autopilot['autoUpgradePolicy']['throughputPolicy']['incrementPercent']
        )
    if offer_autopilot:
        return ThroughputProperties(
            properties=properties,
            auto_scale_max_throughput=offer_autopilot['maxThroughput']
        )
    return ThroughputProperties(
        offer_throughput=properties["content"]["offerThroughput"],
        properties=properties
    )


def _replace_throughput(
    throughput: Union[int, ThroughputProperties],
    new_throughput_properties: Dict[str, Any]
) -> None:
    if isinstance(throughput, int):
        new_throughput_properties["content"]["offerThroughput"] = throughput
    else:
        try:
            max_throughput = throughput.auto_scale_max_throughput
            increment_percent = throughput.auto_scale_increment_percent
            if max_throughput is not None:
                new_throughput_properties['content']['offerAutopilotSettings']['maxThroughput'] = max_throughput
                if increment_percent:
                    new_throughput_properties['content']['offerAutopilotSettings']['autoUpgradePolicy']['throughputPolicy']['incrementPercent'] = increment_percent  # pylint: disable=line-too-long
                if throughput.offer_throughput:
                    new_throughput_properties["content"]["offerThroughput"] = throughput.offer_throughput
        except AttributeError as e:
            raise TypeError("offer_throughput must be int or an instance of ThroughputProperties") from e


def _internal_resourcetype(resource_type: str) -> str:
    """Partition key is used as the resource type for deleting all items by partition key in other SDKs,
    but the colls (collection) resource type needs to be sent for the feature to work. In order to keep it consistent
    with other SDKs, we switch it here.
    :param str resource_type: the resource type
    :return: the resource type after checking if we're doing partition key delete.
    :rtype: str
    """
    if resource_type.lower() == "partitionkey":
        return "colls"
    return resource_type


def _populate_batch_headers(current_headers: Dict[str, Any]) -> None:
    current_headers[http_constants.HttpHeaders.IsBatchRequest] = True
    current_headers[http_constants.HttpHeaders.IsBatchAtomic] = True
    current_headers[http_constants.HttpHeaders.ShouldBatchContinueOnError] = False


def _format_batch_operations(
    operations: Sequence[Union[Tuple[str, Tuple[Any, ...]], Tuple[str, Tuple[Any, ...], Dict[str, Any]]]]
) -> List[Dict[str, Any]]:
    final_operations = []
    for index, batch_operation in enumerate(operations):
        try:
            operation_type = batch_operation[0]
            args = batch_operation[1]
        except IndexError as e:
            raise IndexError(f"Operation {index} in batch is missing a field.") from e
        try:
            kwargs = batch_operation[2]  # type: ignore[misc]
        except IndexError:
            kwargs = {}

        if len(args) == 1:
            if operation_type.lower() == "create":
                operation = {"operationType": "Create",
                             "resourceBody": args[0]}
            elif operation_type.lower() == "upsert":
                operation = {"operationType": "Upsert",
                             "resourceBody": args[0]}
            elif operation_type.lower() == "read":
                operation = {"operationType": "Read",
                             "id": args[0]}
            elif operation_type.lower() == "delete":
                operation = {"operationType": "Delete",
                             "id": args[0]}
        elif len(args) == 2:
            if operation_type.lower() == "replace":
                operation = {"operationType": "Replace",
                             "id": args[0],
                             "resourceBody": args[1]}
            elif operation_type.lower() == "patch":
                operation = {"operationType": "Patch",
                             "id": args[0],
                             "resourceBody": {"operations": args[1]}}
                filter_predicate = kwargs.pop("filter_predicate", None)
                if filter_predicate is not None:
                    operation["resourceBody"]["condition"] = filter_predicate
        else:
            raise AttributeError(
                f"Operation type or args passed in not recognized for operation with index {index}."
            )

        if_match_etag = kwargs.pop("if_match_etag", None)
        if_none_match_etag = kwargs.pop("if_none_match_etag", None)
        if if_match_etag is not None:
            operation["ifMatch"] = if_match_etag
        elif if_none_match_etag is not None:
            operation["ifNoneMatch"] = if_none_match_etag

        final_operations.append(operation)

    return final_operations


def _set_properties_cache(properties: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "_self": properties.get("_self", None), "_rid": properties.get("_rid", None),
        "partitionKey": properties.get("partitionKey", None)
    }
