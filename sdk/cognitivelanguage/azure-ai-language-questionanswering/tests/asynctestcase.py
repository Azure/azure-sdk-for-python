# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import functools
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from azure.core.credentials import AccessToken
from testcase import QuestionAnsweringTest


class AsyncFakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    async def get_token(self, *args):
        return self.token


class AsyncQuestionAnsweringTest(QuestionAnsweringTest):

    def generate_oauth_token(self):
        if self.is_live:
            from azure.identity.aio import ClientSecretCredential
            return ClientSecretCredential(
                self.get_settings_value("TENANT_ID"),
                self.get_settings_value("CLIENT_ID"),
                self.get_settings_value("CLIENT_SECRET"),
            )
        return self.generate_fake_token()

    def generate_fake_token(self):
        return AsyncFakeTokenCredential()

class QnaAuthoringAsyncHelper:

    async def create_test_project(
        client,
        project_name = "IssacNewton",
        is_deployable = False,
        add_sources = False,
        get_export_url = False,
        delete_old_project = False,
        add_qnas = False,
        **kwargs
    ):
        # create project
        await client.create_project(
            project_name=project_name,
            options={
                "description": "biography of Sir Issac Newton",
                "language": "en",
                "multilingualResource": True,
                "settings": {
                    "defaultAnswer": "no answer"
                }
            })

        # add sources
        if is_deployable or add_sources:
            await QnaAuthoringAsyncHelper.add_sources(client, project_name, **kwargs)

        if get_export_url:
            return await QnaAuthoringAsyncHelper.export_project(client, project_name, delete_project=delete_old_project, **kwargs)

    async def add_sources(client, project_name, **kwargs):
        update_sources_poller = await client.begin_update_sources(
            project_name=project_name,
            sources=[
                {
                    "op": "add",
                    "value": {
                        "displayName": "Issac Newton Bio",
                        "sourceUri": "https://wikipedia.org/wiki/Isaac_Newton",
                        "sourceKind": "url"
                    }
                }
            ],
            **kwargs
        )
        await update_sources_poller.result()

    async def export_project(client, project_name, delete_project=True, **kwargs):
        # export project
        export_poller = await client.begin_export(
            project_name=project_name,
            format="json",
            **kwargs
        )
        result = await export_poller.result()

        # delete old project
        if delete_project:
            delete_poller = await client.begin_delete_project(
                project_name=project_name,
                **kwargs
            )
            await delete_poller.result()

        return result["resultUrl"]