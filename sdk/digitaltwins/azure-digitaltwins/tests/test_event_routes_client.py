# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import unittest

from azure.digitaltwins import EventRoutesClient

import pytest

try:
    from unittest.mock import mock
except ImportError:
    # python < 3.3
    from mock import mock

class TestEventRoutesClient(object):
    def test_constructor(self):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        
        event_routes_client = EventRoutesClient(fake_endpoint, fake_credential)
        assert isinstance(event_routes_client, EventRoutesClient)

    @mock.patch(
        'azure.digitaltwins._generated.operations._event_routes_operations.EventRoutesOperations.get_by_id'
    )
    def test_get_event_route(self, get_by_id):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_event_route_id = 'event_route_id'
        event_routes_client = EventRoutesClient(fake_endpoint, fake_credential)

        event_routes_client.get_event_route(fake_event_route_id)
        get_by_id.assert_called_with(
            fake_event_route_id
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._event_routes_operations.EventRoutesOperations.get_by_id'
    )
    def test_get_event_rout_with_kwargs(self, get_by_id):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_event_route_id = 'event_route_id'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        event_routes_client = EventRoutesClient(fake_endpoint, fake_credential)

        event_routes_client.get_event_route(fake_event_route_id, **fake_kwargs)
        get_by_id.assert_called_with(
            fake_event_route_id,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._event_routes_operations.EventRoutesOperations.list'
    )
    def test_list_event_routes(self, list):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        event_routes_client = EventRoutesClient(fake_endpoint, fake_credential)

        event_routes_client.list_event_routes()
        list.assert_called_with(
            {'max_item_count': -1}
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._event_routes_operations.EventRoutesOperations.list'
    )
    def test_list_event_routes_with_max_item_count(self, list):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_max_item_count = 42
        event_routes_client = EventRoutesClient(fake_endpoint, fake_credential)

        event_routes_client.list_event_routes(fake_max_item_count)
        list.assert_called_with(
            {'max_item_count': fake_max_item_count}
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._event_routes_operations.EventRoutesOperations.list'
    )
    def test_list_event_routes_with_kwargs(self, list):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_max_item_count = 42
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        event_routes_client = EventRoutesClient(fake_endpoint, fake_credential)

        event_routes_client.list_event_routes(fake_max_item_count, **fake_kwargs)
        list.assert_called_with(
            {'max_item_count': fake_max_item_count},
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._event_routes_operations.EventRoutesOperations.add'
    )
    def test_upsert_event_route(self, add):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_event_route_id = 'event_route_id'
        fake_event_route = 'event_route'
        event_routes_client = EventRoutesClient(fake_endpoint, fake_credential)

        event_routes_client.upsert_event_route(fake_event_route_id, fake_event_route)
        add.assert_called_with(
            fake_event_route_id,
            fake_event_route
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._event_routes_operations.EventRoutesOperations.add'
    )
    def test_upsert_event_route_with_kwargs(self, add):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_event_route_id = 'event_route_id'
        fake_event_route = 'event_route'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        event_routes_client = EventRoutesClient(fake_endpoint, fake_credential)

        event_routes_client.upsert_event_route(fake_event_route_id, fake_event_route, **fake_kwargs)
        add.assert_called_with(
            fake_event_route_id,
            fake_event_route,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._event_routes_operations.EventRoutesOperations.delete'
    )
    def test_list_event_routes(self, delete):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_event_route_id = 'event_route_id'
        event_routes_client = EventRoutesClient(fake_endpoint, fake_credential)

        event_routes_client.delete_event_route(fake_event_route_id)
        delete.assert_called_with(
            fake_event_route_id
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._event_routes_operations.EventRoutesOperations.delete'
    )
    def test_list_event_routes_with_kwargs(self, delete):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_event_route_id = 'event_route_id'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        event_routes_client = EventRoutesClient(fake_endpoint, fake_credential)

        event_routes_client.delete_event_route(fake_event_route_id, **fake_kwargs)
        delete.assert_called_with(
            fake_event_route_id,
            **fake_kwargs
        )
