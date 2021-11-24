# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from devtools_testutils import AzureTestCase
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.metricsadvisor.models import (
    EmailNotificationHook,
    WebNotificationHook,
)
from base_testcase_async import TestMetricsAdvisorAdministrationClientBaseAsync


class TestMetricsAdvisorAdministrationClientAsync(TestMetricsAdvisorAdministrationClientBaseAsync):

    @AzureTestCase.await_prepared_test
    async def test_create_email_hook(self):
        email_hook_name = self.create_random_name("testemailhookasync")
        async with self.admin_client:
            try:
                email_hook = await self.admin_client.create_hook(
                    hook=EmailNotificationHook(
                        name=email_hook_name,
                        emails_to_alert=["yournamehere@microsoft.com"],
                        description="my email hook",
                        external_link="external link"
                    )
                )
                assert email_hook.id is not None
                assert email_hook.name is not None
                assert email_hook.admins is not None
                assert email_hook.emails_to_alert ==  ["yournamehere@microsoft.com"]
                assert email_hook.description ==  "my email hook"
                assert email_hook.external_link ==  "external link"
                assert email_hook.hook_type ==  "Email"
            finally:
                await self.admin_client.delete_hook(email_hook.id)

                with pytest.raises(ResourceNotFoundError):
                    await self.admin_client.get_hook(email_hook.id)

    @AzureTestCase.await_prepared_test
    async def test_create_web_hook(self):
        web_hook_name = self.create_random_name("testwebhookasync")
        async with self.admin_client:
            try:
                web_hook = await self.admin_client.create_hook(
                    hook=WebNotificationHook(
                        name=web_hook_name,
                        endpoint="https://httpbin.org/post",
                        description="my web hook",
                        external_link="external link"
                    )
                )
                assert web_hook.id is not None
                assert web_hook.name is not None
                assert web_hook.admins is not None
                assert web_hook.endpoint ==  "https://httpbin.org/post"
                assert web_hook.description ==  "my web hook"
                assert web_hook.external_link ==  "external link"
                assert web_hook.hook_type ==  "Webhook"
            finally:
                await self.admin_client.delete_hook(web_hook.id)

                with pytest.raises(ResourceNotFoundError):
                    await self.admin_client.get_hook(web_hook.id)

    @AzureTestCase.await_prepared_test
    async def test_list_hooks(self):
        async with self.admin_client:
            hooks = self.admin_client.list_hooks()
            hooks_list = []
            async for hook in hooks:
                hooks_list.append(hook)
            assert len(hooks_list) > 0

    @AzureTestCase.await_prepared_test
    async def test_update_email_hook_with_model(self):
        name = self.create_random_name("testwebhook")
        async with self.admin_client:
            try:
                hook = await self._create_email_hook_for_update(name)
                hook.name = "update"
                hook.description = "update"
                hook.external_link = "update"
                hook.emails_to_alert = ["myemail@m.com"]

                await self.admin_client.update_hook(hook)
                updated = await self.admin_client.get_hook(hook.id)
                assert updated.name ==  "update"
                assert updated.description ==  "update"
                assert updated.external_link ==  "update"
                assert updated.emails_to_alert ==  ["myemail@m.com"]

            finally:
                await self.admin_client.delete_hook(hook.id)

    @AzureTestCase.await_prepared_test
    async def test_update_email_hook_with_kwargs(self):
        name = self.create_random_name("testhook")
        async with self.admin_client:
            try:
                hook = await self._create_email_hook_for_update(name)
                await self.admin_client.update_hook(
                    hook.id,
                    hook_type="Email",
                    name="update",
                    description="update",
                    external_link="update",
                    emails_to_alert=["myemail@m.com"]
                )
                updated = await self.admin_client.get_hook(hook.id)
                assert updated.name ==  "update"
                assert updated.description ==  "update"
                assert updated.external_link ==  "update"
                assert updated.emails_to_alert ==  ["myemail@m.com"]

            finally:
                await self.admin_client.delete_hook(hook.id)

    @AzureTestCase.await_prepared_test
    async def test_update_email_hook_with_model_and_kwargs(self):
        name = self.create_random_name("testhook")
        async with self.admin_client:
            try:
                hook = await self._create_email_hook_for_update(name)

                hook.name = "don't update me"
                hook.description = "don't update me"
                hook.emails_to_alert = []
                await self.admin_client.update_hook(
                    hook,
                    hook_type="Email",
                    name="update",
                    description="update",
                    external_link="update",
                    emails_to_alert=["myemail@m.com"]
                )
                updated = await self.admin_client.get_hook(hook.id)
                assert updated.name ==  "update"
                assert updated.description ==  "update"
                assert updated.external_link ==  "update"
                assert updated.emails_to_alert ==  ["myemail@m.com"]

            finally:
                await self.admin_client.delete_hook(hook.id)

    @AzureTestCase.await_prepared_test
    async def test_update_email_hook_by_resetting_properties(self):
        name = self.create_random_name("testhook")
        async with self.admin_client:
            try:
                hook = await self._create_email_hook_for_update(name)
                await self.admin_client.update_hook(
                    hook.id,
                    hook_type="Email",
                    name="reset",
                    description=None,
                    external_link=None,
                )
                updated = await self.admin_client.get_hook(hook.id)
                assert updated.name ==  "reset"

                # sending null, but not clearing properties
                # assert updated.description ==  ""
                # assert updated.external_link ==  ""

            finally:
                await self.admin_client.delete_hook(hook.id)

    @AzureTestCase.await_prepared_test
    async def test_update_web_hook_with_model(self):
        name = self.create_random_name("testwebhook")
        async with self.admin_client:
            try:
                hook = await self._create_web_hook_for_update(name)
                hook.name = "update"
                hook.description = "update"
                hook.external_link = "update"
                hook.username = "myusername"
                hook.password = "password"

                await self.admin_client.update_hook(hook)
                updated = await self.admin_client.get_hook(hook.id)
                assert updated.name ==  "update"
                assert updated.description ==  "update"
                assert updated.external_link ==  "update"
                assert updated.username ==  "myusername"

            finally:
                await self.admin_client.delete_hook(hook.id)

    @AzureTestCase.await_prepared_test
    async def test_update_web_hook_with_kwargs(self):
        name = self.create_random_name("testwebhook")
        async with self.admin_client:
            try:
                hook = await self._create_web_hook_for_update(name)
                await self.admin_client.update_hook(
                    hook.id,
                    hook_type="Web",
                    endpoint="https://httpbin.org/post",
                    name="update",
                    description="update",
                    external_link="update",
                    username="myusername",
                    password="password"
                )
                updated = await self.admin_client.get_hook(hook.id)
                assert updated.name ==  "update"
                assert updated.description ==  "update"
                assert updated.external_link ==  "update"
                assert updated.username ==  "myusername"

            finally:
                await self.admin_client.delete_hook(hook.id)

    @AzureTestCase.await_prepared_test
    async def test_update_web_hook_with_model_and_kwargs(self):
        name = self.create_random_name("testwebhook")
        async with self.admin_client:
            try:
                hook = await self._create_web_hook_for_update(name)

                hook.name = "don't update me"
                hook.description = "updateMe"
                hook.username = "don't update me"
                hook.password = "don't update me"
                hook.endpoint = "don't update me"
                await self.admin_client.update_hook(
                    hook,
                    hook_type="Web",
                    endpoint="https://httpbin.org/post",
                    name="update",
                    external_link="update",
                    username="myusername",
                    password="password"
                )
                updated = await self.admin_client.get_hook(hook.id)
                assert updated.name ==  "update"
                assert updated.description ==  "updateMe"
                assert updated.external_link ==  "update"
                assert updated.username ==  "myusername"

            finally:
                await self.admin_client.delete_hook(hook.id)

    @AzureTestCase.await_prepared_test
    async def test_update_web_hook_by_resetting_properties(self):
        name = self.create_random_name("testhook")
        async with self.admin_client:
            try:
                hook = await self._create_web_hook_for_update(name)
                await self.admin_client.update_hook(
                    hook.id,
                    hook_type="Web",
                    name="reset",
                    description=None,
                    endpoint="https://httpbin.org/post",
                    external_link=None,
                    username="myusername",
                    password=None
                )
                updated = await self.admin_client.get_hook(hook.id)
                assert updated.name ==  "reset"
                assert updated.password ==  ""

                # sending null, but not clearing properties
                # assert updated.description ==  ""
                # assert updated.external_link ==  ""

            finally:
                await self.admin_client.delete_hook(hook.id)
