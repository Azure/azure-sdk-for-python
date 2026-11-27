# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Recorded project PUT/GET/PUT/DELETE contracts against an existing Foundry account."""

import logging
import sys
from contextlib import AsyncExitStack

import pytest

from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.aio import CognitiveServicesManagementClient as AsyncClient
from devtools_testutils import AzureMgmtRecordedTestCase, add_body_key_sanitizer, recorded_by_proxy
from devtools_testutils.aio import recorded_by_proxy_async

from project_test_helpers import (
    LOGGER,
    SANITIZED_PROJECT_NAME,
    ResponseDiagnostics,
    api_version,
    assert_project,
    cleanup_failed,
    configuration,
    project_body,
)


@pytest.fixture(autouse=True)
def project_contract_logging(caplog):
    caplog.set_level(logging.INFO, logger=LOGGER.name)


@pytest.fixture(autouse=True)
def project_polling_sleep(patch_sleep, patch_async_sleep):
    """Keep recorded Retry-After headers from delaying playback."""


@pytest.fixture(scope="module", autouse=True)
def project_recording_sanitizers(test_proxy):
    for path in ("$..systemData.createdBy", "$..systemData.lastModifiedBy"):
        add_body_key_sanitizer(json_path=path, value="sanitized-user")
    for path in ("$..identity.principalId", "$..identity.tenantId"):
        add_body_key_sanitizer(json_path=path, value="00000000-0000-0000-0000-000000000000")


class TestProjectLifecycle(AzureMgmtRecordedTestCase):
    def test_project_lifecycle(self):
        self._project_lifecycle()

    @recorded_by_proxy
    def _project_lifecycle(self, variables=None):
        project_api_version = api_version(self, variables)
        group, account, location, name = configuration(self, variables)
        LOGGER.info("Project contract api_version=%s", project_api_version)
        subscription = self.get_settings_value("SUBSCRIPTION_ID")
        expected_id = (
            f"/subscriptions/{subscription}/resourceGroups/{group}/providers/"
            f"Microsoft.CognitiveServices/accounts/{account}/projects/{name}"
        )
        args = (group, account, name)
        with self.create_mgmt_client(
            CognitiveServicesManagementClient, api_version=project_api_version, logging_enable=False
        ) as client:
            with pytest.raises(ResourceNotFoundError):
                client.projects.get(*args)
            try:
                # Cleanup must also run if a rejected initial response already created a resource.
                created = client.projects.begin_create(
                    *args,
                    project_body(location, "Initial SDK contract test"),
                    raw_response_hook=ResponseDiagnostics(project_api_version, "create"),
                ).result()
                assert_project(created, expected_id, location, "Initial SDK contract test", self.is_live)
                fetched = client.projects.get(*args)
                assert_project(fetched, expected_id, location, "Initial SDK contract test", self.is_live)

                updated = client.projects.begin_create(
                    *args,
                    project_body(location, "Updated SDK contract test"),
                    raw_response_hook=ResponseDiagnostics(project_api_version, "update"),
                ).result()
                assert_project(updated, expected_id, location, "Updated SDK contract test", self.is_live)
                fetched = client.projects.get(*args)
                assert_project(fetched, expected_id, location, "Updated SDK contract test", self.is_live)
            finally:
                original_error = sys.exc_info()[0] is not None
                try:
                    client.projects.begin_delete(
                        *args, raw_response_hook=ResponseDiagnostics(project_api_version, "delete")
                    ).result()
                except ResourceNotFoundError:
                    pass
                except Exception as error:  # Cleanup must not mask a create/poll/assertion failure.
                    cleanup_failed(error, original_error)
            with pytest.raises(ResourceNotFoundError):
                client.projects.get(*args)
        return {"project_name": SANITIZED_PROJECT_NAME, "location": location, "api_version": project_api_version}


class TestProjectLifecycleAsync(AzureMgmtRecordedTestCase):
    @pytest.mark.asyncio
    async def test_project_lifecycle(self):
        await self._project_lifecycle()

    @recorded_by_proxy_async
    async def _project_lifecycle(self, variables=None):
        project_api_version = api_version(self, variables)
        group, account, location, name = configuration(self, variables)
        LOGGER.info("Project contract api_version=%s", project_api_version)
        subscription = self.get_settings_value("SUBSCRIPTION_ID")
        expected_id = (
            f"/subscriptions/{subscription}/resourceGroups/{group}/providers/"
            f"Microsoft.CognitiveServices/accounts/{account}/projects/{name}"
        )
        args = (group, account, name)
        credential = self.get_credential(AsyncClient, is_async=True)
        async with AsyncExitStack() as stack:
            stack.push_async_callback(credential.close)
            client = await stack.enter_async_context(
                self.create_client_from_credential(
                    AsyncClient,
                    credential,
                    subscription_id=subscription,
                    api_version=project_api_version,
                    logging_enable=False,
                )
            )
            with pytest.raises(ResourceNotFoundError):
                await client.projects.get(*args)
            try:
                poller = await client.projects.begin_create(
                    *args,
                    project_body(location, "Initial SDK contract test"),
                    raw_response_hook=ResponseDiagnostics(project_api_version, "create"),
                )
                created = await poller.result()
                assert_project(created, expected_id, location, "Initial SDK contract test", self.is_live)
                fetched = await client.projects.get(*args)
                assert_project(fetched, expected_id, location, "Initial SDK contract test", self.is_live)

                poller = await client.projects.begin_create(
                    *args,
                    project_body(location, "Updated SDK contract test"),
                    raw_response_hook=ResponseDiagnostics(project_api_version, "update"),
                )
                updated = await poller.result()
                assert_project(updated, expected_id, location, "Updated SDK contract test", self.is_live)
                fetched = await client.projects.get(*args)
                assert_project(fetched, expected_id, location, "Updated SDK contract test", self.is_live)
            finally:
                original_error = sys.exc_info()[0] is not None
                try:
                    poller = await client.projects.begin_delete(
                        *args, raw_response_hook=ResponseDiagnostics(project_api_version, "delete")
                    )
                    await poller.result()
                except ResourceNotFoundError:
                    pass
                except Exception as error:  # Cleanup must not mask a create/poll/assertion failure.
                    cleanup_failed(error, original_error)
            with pytest.raises(ResourceNotFoundError):
                await client.projects.get(*args)
        return {"project_name": SANITIZED_PROJECT_NAME, "location": location, "api_version": project_api_version}
