
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

REGION = 'westus2'


class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    def get_token(self, *args):
        return self.token


class QuestionAnsweringTest(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['Ocp-Apim-Subscription-Key']

    def __init__(self, method_name):
        super(QuestionAnsweringTest, self).__init__(method_name)

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


class GlobalResourceGroupPreparer(AzureMgmtPreparer):
    def __init__(self):
        super(GlobalResourceGroupPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )

    def create_resource(self, name, **kwargs):
        rg = QuestionAnsweringTest._RESOURCE_GROUP
        #if self.is_live:
        #    self.test_class_instance.scrubber.register_name_pair(
        #        rg.name,
        #        "rgname"
        #    )
        #else:
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
        qna_account = QuestionAnsweringTest._QUESTION_ANSWERING_ACCOUNT

        return {
            'location': REGION,
            'resource_group': QuestionAnsweringTest._RESOURCE_GROUP,
            'question_answering_account': qna_account,
            'question_answering_account_key': QuestionAnsweringTest._QUESTION_ANSWERING_KEY,
            'question_answering_project': QuestionAnsweringTest._QUESTION_ANSWERING_PROJECT
        }

class QuestionAnsweringClientPreparer(AzureMgmtPreparer):
    def __init__(self, client_cls, client_kwargs={}, **kwargs):
        super(QuestionAnsweringClientPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )
        self.client_kwargs = client_kwargs
        self.client_cls = client_cls

    def create_resource(self, name, **kwargs):
        client = self.create_qna_client(**kwargs)
        return {"client": client}

    def create_qna_client(self, **kwargs):
        qna_account = self.client_kwargs.pop("question_answering_account", None)
        if qna_account is None:
            qna_account = kwargs.pop("question_answering_account")

        qna_account_key = self.client_kwargs.pop("question_answering_account_key", None)
        if qna_account_key is None:
            qna_account_key = kwargs.pop("question_answering_account_key")

        return self.client_cls(
            qna_account,
            AzureKeyCredential(qna_account_key),
            **self.client_kwargs
        )


@pytest.fixture(scope="session")
def qna_account():
    # test_case = AzureTestCase("__init__")
    # rg_preparer = ResourceGroupPreparer(random_name_enabled=True, name_prefix='pycog')
    # qna_preparer = CognitiveServicesAccountPreparer(
    #     random_name_enabled=True, name_prefix='pycog', location=REGION
    # )

    try:
        # rg_name, rg_kwargs = rg_preparer._prepare_create_resource(test_case)
        QuestionAnsweringTest._RESOURCE_GROUP = "rgname"  # rg_kwargs['resource_group']
        try:
            # qna_name, qna_kwargs = qna_preparer._prepare_create_resource(test_case, **rg_kwargs)
            QuestionAnsweringTest._QUESTION_ANSWERING_ACCOUNT = os.environ["QNA_ACCOUNT"]  # qna_kwargs['cognitiveservices_account']
            QuestionAnsweringTest._QUESTION_ANSWERING_KEY = os.environ["QNA_KEY"]  # qna_kwargs['cognitiveservices_account_key']
            QuestionAnsweringTest._QUESTION_ANSWERING_PROJECT = os.environ["QNA_PROJECT"]
            yield
        finally:
            # qna_preparer.remove_resource(
            #     qna_name,
            #     resource_group=rg_kwargs['resource_group']
            # )
            QuestionAnsweringTest._QUESTION_ANSWERING_ACCOUNT = None
            QuestionAnsweringTest._QUESTION_ANSWERING_KEY = None
            QuestionAnsweringTest._QUESTION_ANSWERING_PROJECT = None
    finally:
        # rg_preparer.remove_resource(rg_name)
        QuestionAnsweringTest._RESOURCE_GROUP = None
