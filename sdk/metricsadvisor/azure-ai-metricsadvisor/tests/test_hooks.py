# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import uuid
import functools
from azure.core.exceptions import ResourceNotFoundError

from azure.ai.metricsadvisor.models import (
    EmailNotificationHook,
    WebNotificationHook,
)
from devtools_testutils import recorded_by_proxy
from azure.ai.metricsadvisor import MetricsAdvisorAdministrationClient
from base_testcase import TestMetricsAdvisorClientBase, MetricsAdvisorClientPreparer, CREDENTIALS, ids
MetricsAdvisorPreparer = functools.partial(MetricsAdvisorClientPreparer, MetricsAdvisorAdministrationClient)


class TestMetricsAdvisorAdministrationClient(TestMetricsAdvisorClientBase):

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_create_email_hook(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        email_hook_name = self.create_random_name("testemailhook")
        if self.is_live:
            variables["email_hook_name"] = email_hook_name
        try:
            email_hook = client.create_hook(
                hook=EmailNotificationHook(
                    name=variables["email_hook_name"],
                    emails_to_alert=["yournamehere@microsoft.com"],
                    description="my email hook",
                    external_link="external link"
                )
            )
            if self.is_live:
                variables["email_hook_id"] = email_hook.id
            assert email_hook.id is not None
            assert email_hook.name is not None
            assert email_hook.admins is not None
            assert email_hook.emails_to_alert == ["yournamehere@microsoft.com"]
            assert email_hook.description == "my email hook"
            assert email_hook.external_link == "external link"
            assert email_hook.hook_type == "Email"

        finally:
            self.clean_up(client.delete_hook, variables, key="email_hook_id")

            with pytest.raises(ResourceNotFoundError):
                client.get_hook(variables["email_hook_id"])
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_create_web_hook(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        web_hook_name = self.create_random_name("testwebhook")
        if self.is_live:
            variables["web_hook_name"] = web_hook_name
        try:
            web_hook = client.create_hook(
                hook=WebNotificationHook(
                    name=variables["web_hook_name"],
                    endpoint="https://httpbin.org/post",
                    description="my web hook",
                    external_link="external link"
                )
            )
            if self.is_live:
                variables["web_hook_id"] = web_hook.id
            assert web_hook.id is not None
            assert web_hook.name is not None
            assert web_hook.admins is not None
            assert web_hook.endpoint == "https://httpbin.org/post"
            assert web_hook.description == "my web hook"
            assert web_hook.external_link == "external link"
            assert web_hook.hook_type == "Webhook"
        finally:
            self.clean_up(client.delete_hook, variables, key="web_hook_id")

            with pytest.raises(ResourceNotFoundError):
                client.get_hook(variables["web_hook_id"])
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_hooks(self, **kwargs):
        client = kwargs.pop("client")
        hooks = client.list_hooks()
        assert len(list(hooks)) > 0

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(email_hook=True)
    @recorded_by_proxy
    def test_update_email_hook_with_model(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        hook = client.get_hook(variables["email_hook_id"])
        try:
            update_name = "update" + str(uuid.uuid4())
            if self.is_live:
                variables["hook_updated_name"] = update_name
            hook.name = variables["hook_updated_name"]
            hook.description = "update"
            hook.external_link = "update"
            hook.emails_to_alert = ["myemail@m.com"]

            client.update_hook(hook)
            updated = client.get_hook(variables["email_hook_id"])

            assert updated.name == variables["hook_updated_name"]
            assert updated.description == "update"
            assert updated.external_link == "update"
            assert updated.emails_to_alert == ["myemail@m.com"]

        finally:
            self.clean_up(client.delete_hook, variables, key="email_hook_id")
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(email_hook=True)
    @recorded_by_proxy
    def test_update_email_hook_with_kwargs(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        try:
            update_name = "update" + str(uuid.uuid4())
            if self.is_live:
                variables["hook_updated_name"] = update_name
            client.update_hook(
                variables["email_hook_id"],
                hook_type="Email",
                name=variables["hook_updated_name"],
                description="update",
                external_link="update",
                emails_to_alert=["myemail@m.com"]
            )
            updated = client.get_hook(variables["email_hook_id"])
            assert updated.name == variables["hook_updated_name"]
            assert updated.description == "update"
            assert updated.external_link == "update"
            assert updated.emails_to_alert == ["myemail@m.com"]

        finally:
            self.clean_up(client.delete_hook, variables, key="email_hook_id")
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(email_hook=True)
    @recorded_by_proxy
    def test_update_email_hook_with_model_and_kwargs(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        try:
            update_name = "update" + str(uuid.uuid4())
            if self.is_live:
                variables["hook_updated_name"] = update_name
            hook = client.get_hook(variables["email_hook_id"])
            hook.name = "don't update me"
            hook.description = "don't update me"
            hook.emails_to_alert = []
            client.update_hook(
                hook,
                hook_type="Email",
                name=variables["hook_updated_name"],
                description="update",
                external_link="update",
                emails_to_alert=["myemail@m.com"]
            )
            updated = client.get_hook(variables["email_hook_id"])
            assert updated.name == variables["hook_updated_name"]
            assert updated.description == "update"
            assert updated.external_link == "update"
            assert updated.emails_to_alert == ["myemail@m.com"]

        finally:
            self.clean_up(client.delete_hook, variables, key="email_hook_id")
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(email_hook=True)
    @recorded_by_proxy
    def test_update_email_hook_by_resetting_properties(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        try:
            update_name = "update" + str(uuid.uuid4())
            if self.is_live:
                variables["hook_updated_name"] = update_name
            client.update_hook(
                variables["email_hook_id"],
                hook_type="Email",
                name=variables["hook_updated_name"],
                description=None,
                external_link=None,
            )
            updated = client.get_hook(variables["email_hook_id"])
            assert updated.name == variables["hook_updated_name"]

            # sending null, but not clearing properties
            # assert updated.description == ""
            # assert updated.external_link == ""

        finally:
            self.clean_up(client.delete_hook, variables, key="email_hook_id")
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(web_hook=True)
    @recorded_by_proxy
    def test_update_web_hook_with_model(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        try:
            update_name = "update" + str(uuid.uuid4())
            if self.is_live:
                variables["hook_updated_name"] = update_name
            hook = client.get_hook(variables["web_hook_id"])
            hook.name = variables["hook_updated_name"]
            hook.description = "update"
            hook.external_link = "update"
            hook.username = "myusername"
            hook.password = "password"

            client.update_hook(hook)
            updated = client.get_hook(variables["web_hook_id"])
            assert updated.name == variables["hook_updated_name"]
            assert updated.description == "update"
            assert updated.external_link == "update"
            assert updated.username == "myusername"

        finally:
            self.clean_up(client.delete_hook, variables, key="web_hook_id")
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(web_hook=True)
    @recorded_by_proxy
    def test_update_web_hook_with_kwargs(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        try:
            update_name = "update" + str(uuid.uuid4())
            if self.is_live:
                variables["hook_updated_name"] = update_name
            client.update_hook(
                variables["web_hook_id"],
                hook_type="Web",
                endpoint="https://httpbin.org/post",
                name=variables["hook_updated_name"],
                description="update",
                external_link="update",
                username="myusername",
                password="password"
            )
            updated = client.get_hook(variables["web_hook_id"])
            assert updated.name == variables["hook_updated_name"]
            assert updated.description == "update"
            assert updated.external_link == "update"
            assert updated.username == "myusername"

        finally:
            self.clean_up(client.delete_hook, variables, key="web_hook_id")
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(web_hook=True)
    @recorded_by_proxy
    def test_update_web_hook_with_model_and_kwargs(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        try:
            update_name = "update" + str(uuid.uuid4())
            if self.is_live:
                variables["hook_updated_name"] = update_name
            hook = client.get_hook(variables["web_hook_id"])
            hook.name = "don't update me"
            hook.description = "updateMe"
            hook.username = "don't update me"
            hook.password = "don't update me"
            hook.endpoint = "don't update me"
            client.update_hook(
                hook,
                hook_type="Web",
                endpoint="https://httpbin.org/post",
                name=variables["hook_updated_name"],
                external_link="update",
                username="myusername",
                password="password"
            )
            updated = client.get_hook(variables["web_hook_id"])
            assert updated.name == variables["hook_updated_name"]
            assert updated.description == "updateMe"
            assert updated.external_link == "update"
            assert updated.username == "myusername"

        finally:
            self.clean_up(client.delete_hook, variables, key="web_hook_id")
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(web_hook=True)
    @recorded_by_proxy
    def test_update_web_hook_by_resetting_properties(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        try:
            update_name = "update" + str(uuid.uuid4())
            if self.is_live:
                variables["hook_updated_name"] = update_name
            client.update_hook(
                variables["web_hook_id"],
                hook_type="Web",
                name=variables["hook_updated_name"],
                description=None,
                endpoint="https://httpbin.org/post",
                external_link=None,
                username="myusername",
                password=None
            )
            updated = client.get_hook(variables["web_hook_id"])
            assert updated.name == variables["hook_updated_name"]
            assert updated.password == ""

            # sending null, but not clearing properties
            # assert updated.description == ""
            # assert updated.external_link == ""

        finally:
            self.clean_up(client.delete_hook, variables, key="web_hook_id")
        return variables
