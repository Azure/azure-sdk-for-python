# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

from contextlib import contextmanager
from unittest.mock import patch
from urllib.parse import urlsplit, urlunsplit

from azure.cosmos import CosmosClient, DatabaseAccount
from azure.cosmos._global_endpoint_manager import _GlobalEndpointManager


def configure_retry_regions(location_cache, read_regions, write_regions=None):
    """Build a complete synthetic topology, including the derived routing maps."""
    write_regions = list(write_regions or read_regions[:1])
    account = DatabaseAccount()
    account._ReadableLocations = [
        {"name": region, "databaseAccountEndpoint": retry_endpoint(region)} for region in read_regions
    ]
    account._WritableLocations = [
        {"name": region, "databaseAccountEndpoint": retry_endpoint(region)} for region in write_regions
    ]
    account._EnableMultipleWritableLocations = len(write_regions) > 1
    location_cache.connection_policy.PreferredLocations = list(read_regions)
    location_cache.connection_policy.UseMultipleWriteLocations = len(write_regions) > 1
    location_cache.enable_multiple_writable_locations = len(write_regions) > 1
    location_cache.location_unavailability_info_by_endpoint.clear()
    location_cache.perform_on_database_account_read(account)


def retry_endpoint(region):
    return "https://{}.retry-test.invalid/".format(region.lower().replace(" ", ""))


def send_to_test_host(send, host, request, **kwargs):
    """Keep synthetic routing observable to policies, but never send it over the network."""
    url = request.url
    parsed = urlsplit(url)
    rewritten = False
    if parsed.hostname and parsed.hostname.endswith(".retry-test.invalid"):
        target = urlsplit(host)
        request.url = urlunsplit((target.scheme, target.netloc, parsed.path, parsed.query, parsed.fragment))
        rewritten = True
    try:
        if rewritten:
            # The synthetic hostname is rewritten to the real (emulator) host, which uses a
            # self-signed certificate. The caller may already have resolved connection_verify
            # based on the (synthetic) hostname, so force it off here regardless.
            kwargs["connection_verify"] = False
        return send(request, **kwargs)
    finally:
        request.url = url


@contextmanager
def retry_test_client(host, key):
    # Prevent startup health checks from racing the synthetic topology installed below.
    with patch.object(_GlobalEndpointManager, "_start_background_refresh"):
        client = CosmosClient(host, key)
    try:
        manager = client.client_connection._global_endpoint_manager
        transport = client.client_connection.pipeline_client._pipeline._transport
        send = transport.send
        with patch.object(manager, "refresh_endpoint_list"), patch.object(
            transport,
            "send",
            side_effect=lambda request, **kwargs: send_to_test_host(send, host, request, **kwargs),
        ):
            yield client
    finally:
        client.close()
