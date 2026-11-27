# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Recorded account and project Custom Keys connection lifecycle tests."""

import logging
import os
import sys

import pytest

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient, models
from azure.mgmt.cognitiveservices.aio import CognitiveServicesManagementClient as AsyncCognitiveServicesManagementClient
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy
from devtools_testutils.aio import recorded_by_proxy_async

from connection_test_utils import (
    API_VERSION,
    SANITIZED_CONNECTION_NAME,
    add_connection_sanitizers,
    assert_connection,
    connection_resource,
    custom_keys_properties,
    log_create_failure,
)

SANITIZED_RESOURCE_GROUP = "sanitized-resource-group"
SANITIZED_ACCOUNT_NAME = "sanitized-cognitive-account"
SANITIZED_PROJECT_NAME = "sanitized-project"
_LOGGER = logging.getLogger(__name__)


class TestConnectionsLive(AzureMgmtRecordedTestCase):
    def setup_method(self, method):  # pylint: disable=unused-argument
        self.resource_group_name = _live_value(self, "AZURE_RESOURCE_GROUP", SANITIZED_RESOURCE_GROUP)
        self.account_name = _live_value(self, "AZURE_COGNITIVE_SERVICES_ACCOUNT", SANITIZED_ACCOUNT_NAME)

    def test_account_connection_lifecycle(self):
        self._connection_lifecycle("account")

    def test_project_connection_lifecycle(self):
        self._connection_lifecycle("project")

    @pytest.mark.asyncio
    async def test_account_connection_lifecycle_async(self):
        await self._connection_lifecycle_async("account")

    @pytest.mark.asyncio
    async def test_project_connection_lifecycle_async(self):
        await self._connection_lifecycle_async("project")

    @recorded_by_proxy
    def _connection_lifecycle(self, scope, variables=None):
        self._check_api_version(variables)
        parent_args, resource_type, id_suffix = self._scope_parameters(scope)
        with self.create_mgmt_client(CognitiveServicesManagementClient, api_version=API_VERSION) as client:
            self._run_sync_lifecycle(getattr(client, f"{scope}_connections"), parent_args, resource_type, id_suffix)
        return {"api_version": API_VERSION}

    @recorded_by_proxy_async
    async def _connection_lifecycle_async(self, scope, variables=None):
        self._check_api_version(variables)
        parent_args, resource_type, id_suffix = self._scope_parameters(scope)
        async with self.create_mgmt_client(
            AsyncCognitiveServicesManagementClient, is_async=True, api_version=API_VERSION
        ) as client:
            await self._run_async_lifecycle(
                getattr(client, f"{scope}_connections"), parent_args, resource_type, id_suffix
            )
        return {"api_version": API_VERSION}

    def _scope_parameters(self, scope):
        parent_args = (self.resource_group_name, self.account_name)
        resource_type = "Microsoft.CognitiveServices/accounts"
        id_suffix = f"/accounts/{self.account_name}"
        if scope == "project":
            project_name = _live_value(self, "AZURE_COGNITIVE_SERVICES_PROJECT", SANITIZED_PROJECT_NAME)
            parent_args += (project_name,)
            resource_type += "/projects"
            id_suffix += f"/projects/{project_name}"
        return parent_args, f"{resource_type}/connections", f"{id_suffix}/connections"

    def _check_api_version(self, variables):
        if not self.is_live and (not variables or variables.get("api_version") != API_VERSION):
            pytest.fail("Re-record the connection tests with the configured stable API version.")

    def _run_sync_lifecycle(self, operations, parent_args, resource_type, id_suffix):
        connection_name = self.get_resource_name("sdkconn")[:33]
        add_connection_sanitizers(connection_name)
        expected_name = connection_name if self.is_live else SANITIZED_CONNECTION_NAME
        created = False
        expected_id_suffix = f"{id_suffix}/{connection_name}"

        try:
            with pytest.raises(ResourceNotFoundError):
                operations.get(*parent_args, connection_name)

            created = True
            try:
                connection = operations.create(
                    *parent_args,
                    connection_name,
                    connection_resource("initial"),
                )
            except HttpResponseError as error:
                log_create_failure(error, API_VERSION)
                raise

            self._assert_connection(connection, expected_name, resource_type, "initial", expected_id_suffix)
            fetched = operations.get(*parent_args, connection_name)
            self._assert_connection(fetched, expected_name, resource_type, "initial", expected_id_suffix)

            listed = list(operations.list(*parent_args))
            assert any(item.name == expected_name for item in listed)

            updated = operations.update(
                *parent_args,
                connection_name,
                self._update_content("updated"),
            )
            self._assert_connection(updated, expected_name, resource_type, "updated", expected_id_suffix)

            fetched = operations.get(*parent_args, connection_name)
            self._assert_connection(fetched, expected_name, resource_type, "updated", expected_id_suffix)

            operations.delete(*parent_args, connection_name)
            with pytest.raises(ResourceNotFoundError):
                operations.get(*parent_args, connection_name)
            created = False
        finally:
            original_error = sys.exc_info()[1]
            if created:
                try:
                    operations.delete(*parent_args, connection_name)
                except ResourceNotFoundError:
                    pass
                except Exception as cleanup_error:
                    if original_error is None:
                        raise
                    _LOGGER.error(
                        "Connection cleanup failed; preserving the original test failure (cleanup error type: %s)",
                        type(cleanup_error).__name__,
                    )

    async def _run_async_lifecycle(self, operations, parent_args, resource_type, id_suffix):
        connection_name = self.get_resource_name("sdkconn")[:33]
        add_connection_sanitizers(connection_name)
        expected_name = connection_name if self.is_live else SANITIZED_CONNECTION_NAME
        created = False
        expected_id_suffix = f"{id_suffix}/{connection_name}"

        try:
            with pytest.raises(ResourceNotFoundError):
                await operations.get(*parent_args, connection_name)

            created = True
            try:
                connection = await operations.create(
                    *parent_args,
                    connection_name,
                    connection_resource("initial"),
                )
            except HttpResponseError as error:
                log_create_failure(error, API_VERSION)
                raise

            self._assert_connection(connection, expected_name, resource_type, "initial", expected_id_suffix)
            fetched = await operations.get(*parent_args, connection_name)
            self._assert_connection(fetched, expected_name, resource_type, "initial", expected_id_suffix)

            listed = [item async for item in operations.list(*parent_args)]
            assert any(item.name == expected_name for item in listed)

            updated = await operations.update(
                *parent_args,
                connection_name,
                self._update_content("updated"),
            )
            self._assert_connection(updated, expected_name, resource_type, "updated", expected_id_suffix)

            fetched = await operations.get(*parent_args, connection_name)
            self._assert_connection(fetched, expected_name, resource_type, "updated", expected_id_suffix)

            await operations.delete(*parent_args, connection_name)
            with pytest.raises(ResourceNotFoundError):
                await operations.get(*parent_args, connection_name)
            created = False
        finally:
            original_error = sys.exc_info()[1]
            if created:
                try:
                    await operations.delete(*parent_args, connection_name)
                except ResourceNotFoundError:
                    pass
                except Exception as cleanup_error:
                    if original_error is None:
                        raise
                    _LOGGER.error(
                        "Connection cleanup failed; preserving the original test failure (cleanup error type: %s)",
                        type(cleanup_error).__name__,
                    )

    @staticmethod
    def _update_content(revision):
        return models.ConnectionUpdateContent(properties=custom_keys_properties(revision))

    def _assert_connection(self, connection, expected_name, resource_type, revision, expected_id_suffix):
        assert_connection(
            connection,
            expected_name,
            resource_type,
            revision,
            expected_id_suffix,
            self.is_live,
        )


def _live_value(test_case, name, playback_value):
    if not test_case.is_live:
        return playback_value
    value = os.environ.get(name)
    if not value:
        pytest.fail(f"Set {name} before running the live connection tests.")
    return value
