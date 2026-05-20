# The MIT License (MIT)
# Copyright (c) 2021 Microsoft Corporation

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

import logging
from typing import Any, Optional, Tuple

from azure.cosmos import _base, http_constants
from azure.cosmos._constants import _Constants as Constants

# pylint: disable=protected-access

_LOGGER = logging.getLogger(__name__)

class _PartitionKeyRangeGoneRetryPolicyBase:
    """Base class with shared logic for partition key range gone retry policies."""

    def __init__(self, client, *args, **kwargs):
        self.retry_after_in_milliseconds = 1000
        self.refresh_partition_key_range_cache = True
        self.args = args
        self.client = client
        self.exception = None
        self.kwargs = kwargs

    def _extract_collection_info(self):
        """Extract collection link and RID from request.

        :return: A tuple of (collection_link, container_rid). Either or both may be None.
        :rtype: tuple[str, str]
        """
        collection_link = None
        container_rid = None
        if len(self.args) > 3:
            request = self.args[3]
            if hasattr(request, 'headers'):
                container_rid = request.headers.get(http_constants.HttpHeaders.IntendedCollectionRID)
                cached_properties = self.client._container_properties_cache.get(container_rid)
                if cached_properties:
                    collection_link = cached_properties.get("container_link")
        return collection_link, container_rid

    def _get_previous_routing_map(self, collection_link):
        """Gets the cached routing map for a specific collection.

        This method safely navigates the client's internal structure to retrieve
        the last known routing map for a given collection link. It is designed to
        be resilient to missing attributes, returning None if the routing map
        provider or the specific map for the collection is not found.

        :param str collection_link: The link to the collection for which to retrieve the routing map.
        :return: The cached CollectionRoutingMap if it exists, otherwise None.
        :rtype: azure.cosmos.routing.collection_routing_map.CollectionRoutingMap or None
        """
        if collection_link and hasattr(self.client, '_routing_map_provider'):
            if hasattr(self.client._routing_map_provider, '_collection_routing_map_by_item'):
                lookup_key = collection_link
                try:
                    lookup_key = _base.GetResourceIdOrFullNameFromLink(collection_link)
                except Exception:  # pylint: disable=broad-except
                    # Keep existing resilient behavior for unexpected link formats.
                    _LOGGER.debug(
                        "Could not normalize collection_link '%s'; using raw value.",
                        collection_link,
                    )
                return self.client._routing_map_provider._collection_routing_map_by_item.get(lookup_key)
        return None

    def pop_refresh_context(self) -> Tuple[Optional[str], Optional[Any], Optional[dict[str, Any]]]:
        """Return one-time routing-map refresh context for 410 handling.

        This keeps the policy as a state holder while letting retry utilities
        decide if/when to execute I/O.

        :return: A one-time tuple containing the collection link, prior routing
            map, and optional feed options for refreshing the routing map.
        :rtype: tuple[str | None, Any | None, dict[str, Any] | None]
        """
        if not self.refresh_partition_key_range_cache:
            return None, None, None

        collection_link, container_rid = self._extract_collection_info()
        previous_routing_map = self._get_previous_routing_map(collection_link)
        feed_options: Optional[dict[str, Any]] = (
            {Constants.ContainerRID: container_rid} if container_rid else None
        )

        self.refresh_partition_key_range_cache = False
        return collection_link, previous_routing_map, feed_options
