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
import datetime
import json
import uuid
import binascii
from typing import Dict, Any

from urllib.parse import quote as urllib_quote
from urllib.parse import urlsplit

from azure.core import MatchConditions

from . import auth
from . import documents
from . import partition_key
from . import http_constants
from . import _runtime_constants

# pylint: disable=protected-access

_COMMON_OPTIONS = {
    'initial_headers': 'initialHeaders',
    'pre_trigger_include': 'preTriggerInclude',
    'post_trigger_include': 'postTriggerInclude',
    'max_item_count': 'maxItemCount',
    'access_condition': 'accessCondition',
    'indexing_directive': 'indexingDirective',
    'consistency_level': 'consistencyLevel',
    'session_token': 'sessionToken',
    'enable_scan_in_query': 'enableScanInQuery',
    'resource_token_expiry_seconds': 'resourceTokenExpirySeconds',
    'offer_type': 'offerType',
    'offer_throughput': 'offerThroughput',
    'partition_key': 'partitionKey',
    'enable_cross_partition_query': 'enableCrossPartitionQuery',
    'populate_query_metrics': 'populateQueryMetrics',
    'enable_script_logging': 'enableScriptLogging',
    'offer_enable_ru_per_minute_throughput': 'offerEnableRUPerMinuteThroughput',
    'disable_ru_per_minute_usage': 'disableRUPerMinuteUsage',
    'change_feed': 'changeFeed',
    'continuation': 'continuation',
    'is_start_from_beginning': 'isStartFromBeginning',
    'populate_partition_key_range_statistics': 'populatePartitionKeyRangeStatistics',
    'populate_quota_info': 'populateQuotaInfo',
    'content_type': 'contentType',
    'is_query_plan_request': 'isQueryPlanRequest',
    'supported_query_features': 'supportedQueryFeatures',
    'query_version': 'queryVersion'
}


def _get_match_headers(kwargs):
    # type: (Dict[str, Any]) -> Tuple(Optional[str], Optional[str])
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


def build_options(kwargs):
    # type: (Dict[str, Any]) -> Dict[str, Any]
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
        cosmos_client_connection,
        default_headers,
        verb,
        path,
        resource_id,
        resource_type,
        options,
        partition_key_range_id=None,
):
    """Gets HTTP request headers.

    :param cosmos_client_connection.CosmosClient cosmos_client:
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

    if cosmos_client_connection._useMultipleWriteLocations:
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
            if default_client_consistency_level == documents.ConsistencyLevel.Session:
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
        if options.get("partitionKey") is partition_key._Undefined:
            headers[http_constants.HttpHeaders.PartitionKey] = [{}]
        # If partitionKey value is Empty, serialize it as [], which is the equivalent sent for migrated collections
        elif options.get("partitionKey") is partition_key._Empty:
            headers[http_constants.HttpHeaders.PartitionKey] = []
        # else serialize using json dumps method which apart from regular values will serialize None into null
        else:
            headers[http_constants.HttpHeaders.PartitionKey] = json.dumps([options["partitionKey"]])

    if options.get("enableCrossPartitionQuery"):
        headers[http_constants.HttpHeaders.EnableCrossPartitionQuery] = options["enableCrossPartitionQuery"]

    if options.get("populateQueryMetrics"):
        headers[http_constants.HttpHeaders.PopulateQueryMetrics] = options["populateQueryMetrics"]

    if cosmos_client_connection.master_key:
        headers[http_constants.HttpHeaders.XDate] = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

    if cosmos_client_connection.master_key or cosmos_client_connection.resource_tokens:
        authorization = auth.get_authorization_header(
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

    if options.get("changeFeed") is True:
        # On REST level, change feed is using IfNoneMatch/ETag instead of continuation.
        if_none_match_value = None
        if options.get("continuation"):
            if_none_match_value = options["continuation"]
        elif options.get("isStartFromBeginning") and not options["isStartFromBeginning"]:
            if_none_match_value = "*"
        if if_none_match_value:
            headers[http_constants.HttpHeaders.IfNoneMatch] = if_none_match_value
        headers[http_constants.HttpHeaders.AIM] = http_constants.HttpHeaders.IncrementalFeedHeaderValue
    else:
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

    return headers


def GetResourceIdOrFullNameFromLink(resource_link):
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


def GenerateGuidId():
    """Gets a random GUID.

    Note that here we use python's UUID generation library. Basically UUID
    is the same as GUID when represented as a string.

    :return:
        The generated random GUID.
    :rtype: str
    """
    return str(uuid.uuid4())


def GetPathFromLink(resource_link, resource_type=""):
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


def IsNameBased(link):
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


def IsMasterResource(resourceType):
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


def IsDatabaseLink(link):
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


def IsItemContainerLink(link):  # pylint: disable=too-many-return-statements
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


def GetItemContainerInfo(self_link, alt_content_path, id_from_response):
    """Given the self link and alt_content_path from the reponse header and
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
                collection_name = alt_content_path + "/colls/" + urllib_quote(id_from_response)
                return collection_id, collection_name
            collection_name = alt_content_path
            return collection_id, collection_name
        raise ValueError(
            "Response Not from Server Partition, self_link: {0}, alt_content_path: {1}, id: {2}".format(
                self_link, alt_content_path, id_from_response
            )
        )

    raise ValueError("Unable to parse document collection link from " + self_link)


def GetItemContainerLink(link):
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


def IndexOfNth(s, value, n):
    """Gets the index of Nth occurance of a given character in a string.

    :param str s: Input string
    :param char value: Input char to be searched.
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


def IsValidBase64String(string_to_validate):
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


def TrimBeginningAndEndingSlashes(path):
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
def ParsePaths(paths):
    if len(paths) != 1:
        raise ValueError("Unsupported paths count.")

    segmentSeparator = "/"
    path = paths[0]
    tokens = []
    currentIndex = 0

    while currentIndex < len(path):
        if path[currentIndex] != segmentSeparator:
            raise ValueError("Invalid path character at index " + currentIndex)

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
                    raise ValueError("Invalid path character at index " + currentIndex)

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


def create_scope_from_url(url):
    parsed_url = urlsplit(url)
    return parsed_url.scheme + "://" + parsed_url.hostname + "/.default"


def validate_cache_staleness_value(max_integrated_cache_staleness):
    int(max_integrated_cache_staleness)  # Will throw error if data type cant be converted to int
    if max_integrated_cache_staleness <= 0:
        raise ValueError("Parameter 'max_integrated_cache_staleness_in_ms' can only be a positive integer.")
