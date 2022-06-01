# coding=utf-8
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


REGION = 'westus2'


class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    def get_token(self, *args):
        return self.token

TEST_ENDPOINT = 'https://test-resource.api.cognitive.microsoft.com'
TEST_KEY = '0000000000000000'
TEST_CONV_PROJECT_NAME = "conv_test"
TEST_CONV_DEPLOYMENT_NAME = "dep_test"
TEST_ORCH_PROJECT_NAME = "orch_test"
TEST_ORCH_DEPLOYMENT_NAME = "dep_test"

class ConversationTest(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['Ocp-Apim-Subscription-Key']

    def __init__(self, method_name):
        super(ConversationTest, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]
        self.scrubber.register_name_pair(os.environ.get("AZURE_CONVERSATIONS_ENDPOINT"), TEST_ENDPOINT)
        self.scrubber.register_name_pair(os.environ.get("AZURE_CONVERSATIONS_KEY"), TEST_KEY)
        self.scrubber.register_name_pair(os.environ.get("AZURE_CONVERSATIONS_PROJECT_NAME"), TEST_CONV_PROJECT_NAME)
        self.scrubber.register_name_pair(os.environ.get("AZURE_CONVERSATIONS_DEPLOYMENT_NAME"), TEST_CONV_DEPLOYMENT_NAME)
        self.scrubber.register_name_pair(os.environ.get("AZURE_CONVERSATIONS_WORKFLOW_PROJECT_NAME"), TEST_ORCH_PROJECT_NAME)
        self.scrubber.register_name_pair(os.environ.get("AZURE_CONVERSATIONS_WORKFLOW_DEPLOYMENT_NAME"), TEST_ORCH_DEPLOYMENT_NAME)


    def generate_fake_token(self):
        return FakeTokenCredential()


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


class GlobalConversationAccountPreparer(AzureMgmtPreparer):
    def __init__(self):
        super(GlobalConversationAccountPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )

    def create_resource(self, name, **kwargs):
        if self.is_live:
            return {
                'location': REGION,
                'resource_group': "rgname",
                'endpoint': os.environ.get("AZURE_CONVERSATIONS_ENDPOINT"),
                'key': os.environ.get("AZURE_CONVERSATIONS_KEY"),
                'conv_project_name': os.environ.get("AZURE_CONVERSATIONS_PROJECT_NAME"),
                'conv_deployment_name': os.environ.get("AZURE_CONVERSATIONS_DEPLOYMENT_NAME"),
                'orch_project_name': os.environ.get("AZURE_CONVERSATIONS_WORKFLOW_PROJECT_NAME"),
                'orch_deployment_name': os.environ.get("AZURE_CONVERSATIONS_WORKFLOW_DEPLOYMENT_NAME")
            }
        return {
            'location': REGION,
            'resource_group': "rgname",
            'endpoint': TEST_ENDPOINT,
            'key': TEST_KEY,
            'conv_project_name': TEST_CONV_PROJECT_NAME,
            'conv_deployment_name': TEST_CONV_DEPLOYMENT_NAME,
            'orch_project_name': TEST_ORCH_PROJECT_NAME,
            'orch_deployment_name': TEST_ORCH_DEPLOYMENT_NAME
        }