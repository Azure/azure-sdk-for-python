# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""End-to-end test against a real Azure Cosmos DB account for issue #46219.

This test demonstrates -- against a live account -- that with
``enable_endpoint_discovery=False`` the SDK only ever issues HTTP requests
to the URL supplied at client construction time, and never falls back to
synthesized regional endpoints such as
``https://<account>-<region>.documents.azure.com`` which on a
private-endpoint-only deployment would resolve via public DNS and be rejected
by the account's firewall with a 403.

Uses the same environment variables as the rest of the test suite:
    ACCOUNT_HOST -- Cosmos account endpoint, e.g. https://myacct.documents.azure.com:443/
    ACCOUNT_KEY  -- Cosmos account master key

The test is skipped when ACCOUNT_HOST points at the emulator since this
scenario only matters for a real, geo-replicated account.
"""

from urllib.parse import urlparse

import pytest
from azure.core.pipeline.transport import RequestsTransport

import test_config
from azure.cosmos import CosmosClient


class RecordingTransport(RequestsTransport):
    """Passes every request through to the network and records its URL.

    Lets the test assert on the full set of endpoints the SDK actually
    contacted, rather than the endpoints the SDK *would have* contacted in a
    mocked-out unit test.
    """

    def __init__(self, **config):
        super().__init__(**config)
        self.urls: list[str] = []

    def send(self, request, **kwargs):
        self.urls.append(request.url)
        return super().send(request, **kwargs)


def _hosts(urls):
    return sorted({urlparse(u).netloc for u in urls})


@pytest.mark.skipif(
    test_config.TestConfig.is_emulator,
    reason="Issue #46219 only manifests against a real, multi-region Cosmos account.",
)
class TestPrivateEndpointReal:
    """Issue #46219 contract verified against a live Cosmos DB account."""

    host = test_config.TestConfig.host
    credential = test_config.TestConfig.masterKey
    database_id = test_config.TestConfig.TEST_DATABASE_ID

    @staticmethod
    def _supplied_host(url: str) -> str:
        return urlparse(url).netloc

    def _exercise(self, client: CosmosClient) -> None:
        """Perform enough work to trigger startup discovery + a few operations."""
        # Read a known database (created by the test session fixture).
        db = client.get_database_client(self.database_id)
        list(db.list_containers())

    def test_discovery_disabled_never_contacts_regional_endpoints(self):
        recorder = RecordingTransport()
        client = CosmosClient(
            self.host,
            credential=self.credential,
            consistency_level="Session",
            enable_endpoint_discovery=False,
            transport=recorder,
        )
        try:
            self._exercise(client)
        finally:
            client.client_connection.pipeline_client.__exit__(None, None, None)

        supplied_host = self._supplied_host(self.host)
        unique_hosts = _hosts(recorder.urls)
        print(f"\n[discovery=False] supplied host: {supplied_host}")
        print(f"[discovery=False] hosts the SDK contacted ({len(recorder.urls)} requests):")
        for h in unique_hosts:
            print(f"  - {h}")

        offenders = [u for u in recorder.urls if self._supplied_host(u) != supplied_host]
        assert not offenders, (
            "enable_endpoint_discovery=False was set, yet the SDK issued requests "
            f"to non-supplied hosts. Offenders:\n  " + "\n  ".join(sorted(set(offenders)))
        )

    def test_discovery_enabled_baseline(self):
        """Companion baseline: with discovery on, show the contacted hosts.

        On a geo-replicated account this typically includes regional FQDNs
        (e.g. ``<account>-<region>.documents.azure.com``); on a single-region
        account it is just the global endpoint. The assertion is intentionally
        loose so this test passes regardless of how the account is provisioned;
        the printed output is what makes the comparison with the disabled-case
        meaningful.
        """
        recorder = RecordingTransport()
        client = CosmosClient(
            self.host,
            credential=self.credential,
            consistency_level="Session",
            enable_endpoint_discovery=True,
            transport=recorder,
        )
        try:
            self._exercise(client)
        finally:
            client.client_connection.pipeline_client.__exit__(None, None, None)

        unique_hosts = _hosts(recorder.urls)
        print(f"\n[discovery=True]  hosts the SDK contacted ({len(recorder.urls)} requests):")
        for h in unique_hosts:
            print(f"  - {h}")

        # The supplied host must always appear (it's what every account read goes to).
        assert self._supplied_host(self.host) in unique_hosts
