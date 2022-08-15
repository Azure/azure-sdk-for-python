
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest

from azure.core.credentials import AccessToken, AzureKeyCredential
from devtools_testutils import (
    AzureTestCase,
    AzureMgmtPreparer,
    FakeResource,
    ResourceGroupPreparer,
)
from devtools_testutils.cognitiveservices_testcase import CognitiveServicesAccountPreparer
from azure_devtools.scenario_tests import ReplayableTest

from azure.ai.language.questionanswering import QuestionAnsweringClient


REGION = 'westus2'


class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    def get_token(self, *args):
        return self.token

TEST_ENDPOINT = 'https://test-resource.api.cognitive.microsoft.com/'
TEST_KEY = '0000000000000000'
TEST_PROJECT = 'test-project'


class QuestionAnsweringTest(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['Ocp-Apim-Subscription-Key']

    def __init__(self, method_name):
        super(QuestionAnsweringTest, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]
        self.scrubber.register_name_pair(os.environ.get("AZURE_QUESTIONANSWERING_ENDPOINT"), TEST_ENDPOINT)
        self.scrubber.register_name_pair(os.environ.get("AZURE_QUESTIONANSWERING_KEY"), TEST_KEY)
        self.scrubber.register_name_pair(os.environ.get("AZURE_QUESTIONANSWERING_PROJECT"), TEST_PROJECT)

    def get_oauth_endpoint(self):
        raise NotImplementedError()

    def generate_oauth_token(self):
        if self.is_live:
            from azure.identity import ClientSecretCredential
            return ClientSecretCredential(
                self.get_settings_value("TENANT_ID"),
                self.get_settings_value("CLIENT_ID"),
                self.get_settings_value("CLIENT_SECRET"),
            )
        return self.generate_fake_token()

    def generate_fake_token(self):
        return FakeTokenCredential()

    @property
    def kwargs_for_polling(self):
        if self.is_playback:
            return {"polling_interval": 0}
        return {}

class GlobalResourceGroupPreparer(AzureMgmtPreparer):
    def __init__(self):
        super(GlobalResourceGroupPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )

    def create_resource(self, name, **kwargs):
        rg = FakeResource(
            name="rgname",
            id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rgname"
        )

        return {
            'location': REGION,
            'resource_group': rg,
        }


class GlobalQuestionAnsweringAccountPreparer(AzureMgmtPreparer):
    def __init__(self):
        super(GlobalQuestionAnsweringAccountPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )

    def create_resource(self, name, **kwargs):
        if self.is_live:
            return {
                'location': REGION,
                'resource_group': "rgname",
                'qna_account': os.environ.get("AZURE_QUESTIONANSWERING_ENDPOINT"),
                'qna_key': os.environ.get("AZURE_QUESTIONANSWERING_KEY"),
                'qna_project': os.environ.get("AZURE_QUESTIONANSWERING_PROJECT")
            }
        return {
            'location': REGION,
            'resource_group': "rgname",
            'qna_account': TEST_ENDPOINT,
            'qna_key': TEST_KEY,
            'qna_project': TEST_PROJECT
        }

class QnaAuthoringHelper:

    def create_test_project(
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
        client.create_project(
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
            QnaAuthoringHelper.add_sources(client, project_name, **kwargs)

        if get_export_url:
            return QnaAuthoringHelper.export_project(client, project_name, delete_project=delete_old_project, **kwargs)

    def add_sources(client, project_name, **kwargs):
        update_sources_poller = client.begin_update_sources(
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
        update_sources_poller.result()

    def export_project(client, project_name, delete_project=True, **kwargs):
        # export project
        export_poller = client.begin_export(
            project_name=project_name,
            format="json",
            **kwargs
        )
        result = export_poller.result()

        # delete old project
        if delete_project:
            delete_poller = client.begin_delete_project(
                project_name=project_name,
                **kwargs
            )
            delete_poller.result()

        return result["resultUrl"]