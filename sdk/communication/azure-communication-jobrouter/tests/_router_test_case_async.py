# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from abc import abstractmethod
from _shared.utils import get_http_logging_policy
from azure.communication.jobrouter.aio import RouterClient
from _router_test_case import RouterTestCaseBase


class AsyncRouterTestCase(RouterTestCaseBase):
    def setUp(self):
        super(AsyncRouterTestCase, self).setUp()

    @abstractmethod
    async def clean_up(self):
        pass

    def tearDown(self):
        super(AsyncRouterTestCase, self).tearDown()

    def create_client(self) -> RouterClient:
        return RouterClient.from_connection_string(
            conn_str = self.connection_str,
            http_logging_policy=get_http_logging_policy())
