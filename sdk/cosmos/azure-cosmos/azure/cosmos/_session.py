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

"""Session Consistency Tracking in the Azure Cosmos database service.
"""

import logging
import sys
import traceback
import threading
from typing import Any, Optional

from . import _base
from . import http_constants
from ._routing.routing_map_provider import SmartRoutingMapProvider
from ._routing.aio.routing_map_provider import SmartRoutingMapProvider as SmartRoutingMapProviderAsync
from ._vector_session_token import VectorSessionToken
from .exceptions import CosmosHttpResponseError
from .partition_key import PartitionKey

# pylint: disable=protected-access,too-many-nested-blocks

logger = logging.getLogger("azure.cosmos.SessionContainer")

class SessionContainer(object):
    def __init__(self):
        self.collection_name_to_rid = {}
        self.rid_to_session_token = {}
        self.session_lock = threading.RLock()

    def get_session_token(
            self,
            resource_path: str,
            pk_value: Any,
            container_properties_cache: dict[str, dict[str, Any]],
            routing_map_provider: SmartRoutingMapProvider,
            partition_key_range_id: Optional[int],
            options: dict[str, Any]
    ) -> str:
        """Get Session Token for the given collection and partition key information.

        :param str resource_path: Self link / path to the resource
        :param ~azure.cosmos.SmartRoutingMapProvider routing_map_provider: routing map containing relevant session
            information, such as partition key ranges for a given collection
        :param Any pk_value: The partition key value being used for the operation
        :param container_properties_cache: Container properties cache used to fetch partition key definitions
        :type container_properties_cache: dict[str, dict[str, Any]]
        :param int partition_key_range_id: The partition key range ID used for the operation
        :param options: Options for the operation calling this method
        :type options: dict[str, Any]
        :return: Session Token dictionary for the collection_id, will be empty string if not found or if the operation
        does not require a session token (single master write operations).
        :rtype: str
        """

        with self.session_lock:
            is_name_based = _base.IsNameBased(resource_path)
            session_token = ""
            collection_name = ""

            try:
                if is_name_based:
                    # get the collection name
                    collection_name = _base.GetItemContainerLink(resource_path)
                    if collection_name in self.collection_name_to_rid:
                        # if the collection name is already in the map, use the rid from there
                        collection_rid = self.collection_name_to_rid[collection_name]
                    else:
                        # if the collection name is not in the map, we need to get the rid from containers cache
                        collection_rid = container_properties_cache.get(collection_name, {}).get("_rid")
                        if collection_rid:
                            self.collection_name_to_rid[collection_name] = collection_rid
                else:
                    collection_rid = _base.GetItemContainerLink(resource_path)

                if collection_rid in self.rid_to_session_token and (collection_name in container_properties_cache or
                                                                    collection_rid in container_properties_cache):
                    token_dict = self.rid_to_session_token[collection_rid]
                    if partition_key_range_id is not None:
                        # if we find a cached session token for the relevant pk range id, use that session token
                        if token_dict.get(partition_key_range_id):
                            vector_session_token = token_dict.get(partition_key_range_id)
                            session_token = "{0}:{1}".format(partition_key_range_id, vector_session_token.session_token)
                        # if we don't find it, we do a session token merge for the parent pk ranges
                        # this should only happen immediately after a partition split
                        else:
                            container_routing_map = \
                                routing_map_provider._collection_routing_map_by_item[collection_name]
                            current_range = container_routing_map._rangeById.get(partition_key_range_id)
                            if current_range is not None:
                                vector_session_token = self._resolve_partition_local_session_token(current_range,
                                                                                                   token_dict)
                                if vector_session_token is not None:
                                    session_token = "{0}:{1}".format(partition_key_range_id, vector_session_token)
                    elif pk_value is not None:
                        collection_pk_definition = container_properties_cache[collection_name]["partitionKey"]
                        partition_key = PartitionKey(path=collection_pk_definition['paths'],
                                                     kind=collection_pk_definition['kind'],
                                                     version=collection_pk_definition['version'])
                        epk_range = partition_key._get_epk_range_for_partition_key(pk_value=pk_value)
                        pk_range = routing_map_provider.get_overlapping_ranges(collection_name,
                                                                               [epk_range],
                                                                               options)
                        if len(pk_range) > 0:
                            partition_key_range_id = pk_range[0]['id']
                            vector_session_token = self._resolve_partition_local_session_token(pk_range, token_dict)
                            if vector_session_token is not None:
                                session_token = "{0}:{1}".format(partition_key_range_id, vector_session_token)
                    else:
                        # we're executing a cross partition streamable query that can be resolved by the gateway
                        # send the entire compound session token for the container to target all partitions
                        # TODO: this logic breaks large containers, needs to be addressed along with requesting
                        #  a query plan for every query
                        session_token_list = []
                        for key in token_dict.keys():
                            session_token_list.append("{0}:{1}".format(key, token_dict[key].convert_to_string()))
                        session_token = ",".join(session_token_list)
                    return session_token
                return ""
            except (KeyError, AttributeError) as e:  # pylint: disable=broad-except
                logger.debug("Error while resolving session token: %s", e)
                return ""

    async def get_session_token_async(
            self,
            resource_path: str,
            pk_value: Any,
            container_properties_cache: dict[str, dict[str, Any]],
            routing_map_provider: SmartRoutingMapProviderAsync,
            partition_key_range_id: Optional[str],
            options: dict[str, Any]
    ) -> str:
        """Get Session Token for the given collection and partition key information.

        :param str resource_path: Self link / path to the resource
        :param ~azure.cosmos.SmartRoutingMapProviderAsync routing_map_provider: routing map containing relevant session
            information, such as partition key ranges for a given collection
        :param Any pk_value: The partition key value being used for the operation
        :param container_properties_cache: Container properties cache used to fetch partition key definitions
        :type container_properties_cache: dict[str, dict[str, Any]]
        :param Any routing_map_provider: The routing map provider containing the partition key range cache logic
        :param str partition_key_range_id: The partition key range ID used for the operation
        :param options: Options for the operation calling this method
        :type options: dict[str, Any]
        :return: Session Token dictionary for the collection_id, will be empty string if not found or if the operation
        does not require a session token (single master write operations).
        :rtype: str
        """

        with self.session_lock:
            is_name_based = _base.IsNameBased(resource_path)
            session_token = ""

            try:
                if is_name_based:
                    # get the collection name
                    collection_name = _base.GetItemContainerLink(resource_path)
                    if collection_name in self.collection_name_to_rid:
                        # if the collection name is already in the map, use the rid from there
                        collection_rid = self.collection_name_to_rid[collection_name]
                    else:
                        # if the collection name is not in the map, we need to get the rid from containers cache
                        collection_rid = container_properties_cache.get(collection_name, {}).get("_rid")
                        if collection_rid:
                            self.collection_name_to_rid[collection_name] = collection_rid
                else:
                    collection_rid = _base.GetItemContainerLink(resource_path)

                if collection_rid in self.rid_to_session_token and (collection_name in container_properties_cache or
                                                                    collection_rid in container_properties_cache):
                    token_dict = self.rid_to_session_token[collection_rid]
                    if partition_key_range_id is not None:
                        # if we find a cached session token for the relevant pk range id, use that session token
                        if token_dict.get(partition_key_range_id):
                            vector_session_token = token_dict.get(partition_key_range_id)
                            session_token = "{0}:{1}".format(partition_key_range_id,
                                                             vector_session_token.session_token)
                        # if we don't find it, we do a session token merge for the parent pk ranges
                        # this should only happen immediately after a partition split
                        else:
                            container_routing_map = \
                                routing_map_provider._collection_routing_map_by_item[collection_name]
                            current_range = container_routing_map._rangeById.get(partition_key_range_id)
                            if current_range is not None:
                                vector_session_token = self._resolve_partition_local_session_token(current_range,
                                                                                                   token_dict)
                                if vector_session_token is not None:
                                    session_token = "{0}:{1}".format(partition_key_range_id, vector_session_token)
                    elif pk_value is not None:
                        collection_pk_definition = container_properties_cache[collection_name]["partitionKey"]
                        partition_key = PartitionKey(path=collection_pk_definition['paths'],
                                                     kind=collection_pk_definition['kind'],
                                                     version=collection_pk_definition['version'])
                        epk_range = partition_key._get_epk_range_for_partition_key(pk_value=pk_value)
                        pk_range = await routing_map_provider.get_overlapping_ranges(collection_name,
                                                                                     [epk_range],
                                                                                     options)
                        if len(pk_range) > 0:
                            partition_key_range_id = pk_range[0]['id']
                            vector_session_token = self._resolve_partition_local_session_token(pk_range, token_dict)
                            if vector_session_token is not None:
                                session_token = "{0}:{1}".format(partition_key_range_id, vector_session_token)
                    else:
                        # we're executing a cross partition streamable query that can be resolved by the gateway
                        # send the entire compound session token for the container to target all partitions
                        # TODO: this logic breaks large containers, needs to be addressed along with requesting
                        #  a query plan for every query
                        session_token_list = []
                        for key in token_dict.keys():
                            session_token_list.append("{0}:{1}".format(key, token_dict[key].convert_to_string()))
                        session_token = ",".join(session_token_list)
                    return session_token
                return ""
            except Exception:  # pylint: disable=broad-except
                return ""

    def set_session_token(self, client_connection, response_result, response_headers):
        """Session token must only be updated from response of requests that
        successfully mutate resource on the server side (write, replace, delete etc).

        :param client_connection: Client connection used to refresh the partition key range cache if needed
        :type client_connection: Union[azure.cosmos.CosmosClientConnection, azure.cosmos.aio.CosmosClientConnection]
        :param dict response_result:
        :param dict response_headers:
        :return: None
        """
        # pylint: disable=too-many-statements

        # there are two pieces of information that we need to update session token-
        # self link which has the rid representation of the resource, and
        # x-ms-alt-content-path which is the string representation of the resource

        with self.session_lock:
            try:
                self_link = response_result.get("_self")

                # extract alternate content path from the response_headers
                # (only document level resource updates will have this),
                # and if not present, then we can assume that we don't have to update
                # session token for this request
                alt_content_path_key = http_constants.HttpHeaders.AlternateContentPath
                response_result_id_key = "id"
                response_result_id = None
                if alt_content_path_key in response_headers:
                    alt_content_path = response_headers[http_constants.HttpHeaders.AlternateContentPath]
                    if response_result_id_key in response_result:
                        response_result_id = response_result[response_result_id_key]
                else:
                    return
                if self_link is not None:
                    collection_rid, collection_name = _base.GetItemContainerInfo(self_link, alt_content_path,
                                                                                response_result_id)
                else:
                    # if for whatever reason we don't have a _self link at this point, we use the container name
                    collection_name = alt_content_path
                    collection_rid = self.collection_name_to_rid.get(collection_name)
                # if the response came in with a new partition key range id after a split, refresh the pk range cache
                partition_key_range_id = response_headers.get(http_constants.HttpHeaders.PartitionKeyRangeID)
                collection_ranges = None
                if client_connection:
                    collection_ranges = \
                        client_connection._routing_map_provider._collection_routing_map_by_item.get(collection_name)
                if collection_ranges and not collection_ranges._rangeById.get(partition_key_range_id):
                    client_connection.refresh_routing_map_provider()
            except ValueError:
                return
            except Exception:  # pylint: disable=broad-except
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
                return

            if collection_name in self.collection_name_to_rid:
                # check if the rid for the collection name has changed
                # this means that potentially, the collection was deleted
                # and recreated
                existing_rid = self.collection_name_to_rid[collection_name]
                if collection_rid != existing_rid:
                    # flush the session tokens for the old rid, and
                    # update the new rid into the collection name to rid map.
                    self.rid_to_session_token[existing_rid] = {}
                    self.collection_name_to_rid[collection_name] = collection_rid

            # parse session token
            parsed_tokens = self.parse_session_token(response_headers)

            # update session token in collection rid to session token map
            if collection_rid in self.rid_to_session_token:
                # we need to update the session tokens for 'this' collection
                for id_ in parsed_tokens:  # pylint: disable=consider-using-dict-items
                    old_session_token = (
                        self.rid_to_session_token[collection_rid][id_]
                        if id_ in self.rid_to_session_token[collection_rid]
                        else None
                    )
                    if not old_session_token:
                        self.rid_to_session_token[collection_rid][id_] = parsed_tokens[id_]
                    else:
                        self.rid_to_session_token[collection_rid][id_] = parsed_tokens[id_].merge(old_session_token)
            else:
                self.rid_to_session_token[collection_rid] = parsed_tokens
            self.collection_name_to_rid[collection_name] = collection_rid

    def clear_session_token(self, response_headers):
        with self.session_lock:
            collection_rid = ""
            alt_content_path = ""
            alt_content_path_key = http_constants.HttpHeaders.AlternateContentPath
            if alt_content_path_key in response_headers:
                alt_content_path = response_headers[http_constants.HttpHeaders.AlternateContentPath]
                if alt_content_path in self.collection_name_to_rid:
                    collection_rid = self.collection_name_to_rid[alt_content_path]
                    del self.collection_name_to_rid[alt_content_path]
                    del self.rid_to_session_token[collection_rid]

    @staticmethod
    def parse_session_token(response_headers):
        """Extracts session token from response headers and parses.

        :param dict response_headers:
        :return: A dictionary of partition id to session lsn for given collection
        :rtype: dict
        """

        # extract session token from response header
        session_token = ""
        if http_constants.HttpHeaders.SessionToken in response_headers:
            session_token = response_headers[http_constants.HttpHeaders.SessionToken]

        id_to_sessionlsn = {}
        if session_token:
            # extract id, lsn from the token. For p-collection,
            # the token will be a concatenation of pairs for each collection
            token_pairs = session_token.split(",")
            for token_pair in token_pairs:
                tokens = token_pair.split(":")
                if len(tokens) == 2:
                    id_ = tokens[0]
                    sessionToken = VectorSessionToken.create(tokens[1])
                    if sessionToken is None:
                        raise CosmosHttpResponseError(
                            status_code=http_constants.StatusCodes.INTERNAL_SERVER_ERROR,
                            message="Could not parse the received session token: %s" % tokens[1],
                        )
                    id_to_sessionlsn[id_] = sessionToken
        return id_to_sessionlsn

    def _resolve_partition_local_session_token(self, pk_range, token_dict):
        parent_session_token = None
        parents = pk_range[0].get('parents').copy()
        parents.append(pk_range[0]['id'])
        for parent in parents:
            session_token = token_dict.get(parent)
            if session_token is not None:
                vector_session_token = session_token.session_token
                if parent_session_token is None:
                    parent_session_token = vector_session_token
                # if initial token is already set, and the next parent's token is cached, merge vector session tokens
                else:
                    vector_token_1 = VectorSessionToken.create(parent_session_token)
                    vector_token_2 = VectorSessionToken.create(vector_session_token)
                    vector_token = vector_token_1.merge(vector_token_2)
                    parent_session_token = vector_token.session_token
        return parent_session_token


class Session(object):
    """State of an Azure Cosmos session.

    This session object can be shared across clients within the same process.

    :param url_connection:
    """

    def __init__(self, url_connection):
        self.url_connection = url_connection
        self.session_container = SessionContainer()
        # include creation time, and some other stats

    def clear_session_token(self, response_headers):
        self.session_container.clear_session_token(response_headers)

    def update_session(self, client_connection, response_result, response_headers):
        self.session_container.set_session_token(client_connection, response_result, response_headers)

    def get_session_token(self, resource_path, pk_value, container_properties_cache, routing_map_provider,
                          partition_key_range_id, options):
        return self.session_container.get_session_token(resource_path, pk_value, container_properties_cache,
                                                        routing_map_provider, partition_key_range_id, options)

    async def get_session_token_async(self, resource_path, pk_value, container_properties_cache, routing_map_provider,
                                      partition_key_range_id, options):
        return await self.session_container.get_session_token_async(resource_path,
                                                                    pk_value,
                                                                    container_properties_cache,
                                                                    routing_map_provider,
                                                                    partition_key_range_id,
                                                                    options)
