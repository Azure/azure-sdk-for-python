# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import uuid

from devtools_testutils import AzureTestCase
from _preparer import DigitalTwinsRGPreparer, DigitalTwinsPreparer

from azure.digitaltwins.core import DigitalTwinsClient, DigitalTwinsEventRoute
from azure.core.exceptions import (
    ResourceNotFoundError,
    HttpResponseError,
    ResourceExistsError,
)


class DigitalTwinsEventRouteTests(AzureTestCase):

    def _get_client(self, endpoint, **kwargs):
        credential = self.get_credential(DigitalTwinsClient)
        return self.create_client_from_credential(
            DigitalTwinsClient,
            credential,
            endpoint=endpoint,
            **kwargs)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_create_event_route_no_endpoint(self, resource_group, location, digitaltwin):
        event_route_id = self.create_random_name('eventRoute-')
        event_filter = "$eventType = 'DigitalTwinTelemetryMessages' or $eventType = 'DigitalTwinLifecycleNotification'"
        endpoint = self.create_random_name('endpoint-')
        route = DigitalTwinsEventRoute(
            endpoint_name=endpoint,
            filter=event_filter
        )
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(HttpResponseError):
            client.upsert_event_route(event_route_id, route)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_get_event_route_not_existing(self, resource_group, location, digitaltwin):
        event_route_id = self.create_random_name('eventRoute-')
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ResourceNotFoundError):
            client.get_event_route(event_route_id)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_list_event_routes(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        all_routes = list(client.list_event_routes())
        assert all_routes == []

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_delete_event_route_not_existing(self, resource_group, location, digitaltwin):
        event_route_id = self.create_random_name('eventRoute-')
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ResourceNotFoundError):
            client.delete_event_route(event_route_id)
