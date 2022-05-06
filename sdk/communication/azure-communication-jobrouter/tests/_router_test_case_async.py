# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from _shared.utils import get_http_logging_policy
from azure.communication.jobrouter.aio import RouterClient
from _router_test_case import RouterTestCaseBase


class AsyncRouterTestCase(RouterTestCaseBase):
    def setUp(self):
        super(AsyncRouterTestCase, self).setUp()

    def create_client(self) -> RouterClient:
        return RouterClient.from_connection_string(
            conn_str = self.connection_str,
            http_logging_policy=get_http_logging_policy())
