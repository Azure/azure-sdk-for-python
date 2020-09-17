# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import unittest

from azure.digitaltwins import QueryClient

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
        
        query_client = QueryClient(fake_endpoint, fake_credential)
        assert isinstance(query_client, QueryClient)

    @mock.patch(
        'azure.digitaltwins._generated.operations._query_operations.QueryOperations.query_twins'
    )
    def test_query_twins(self, query_twins):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_query_specification = 'query_specification'
        query_client = QueryClient(fake_endpoint, fake_credential)

        query_client.query_twins(fake_query_specification)
        query_twins.assert_called_with(
            fake_query_specification
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._query_operations.QueryOperations.query_twins'
    )
    def test_query_twins_with_kwargs(self, query_twins):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_query_specification = 'query_specification'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        query_client = QueryClient(fake_endpoint, fake_credential)

        query_client.query_twins(fake_query_specification, **fake_kwargs)
        query_twins.assert_called_with(
            fake_query_specification,
            **fake_kwargs
        )
