
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from azure.core.credentials import AccessToken
from devtools_testutils import (
    AzureTestCase,
    AzureMgmtPreparer,
    FakeResource,
    ResourceGroupPreparer,
)
from devtools_testutils.cognitiveservices_testcase import CognitiveServicesAccountPreparer
from azure_devtools.scenario_tests import ReplayableTest


class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    def get_token(self, *args):
        return self.token


class FormRecognizerTest(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['Ocp-Apim-Subscription-Key']

    def __init__(self, method_name):
        super(FormRecognizerTest, self).__init__(method_name)

    def get_oauth_endpoint(self):
        return self.get_settings_value("FORM_RECOGNIZER_ENDPOINT")

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
        rg = FormRecognizerTest._RESOURCE_GROUP
        if self.is_live:
            self.test_class_instance.scrubber.register_name_pair(
                rg.name,
                "rgname"
            )
        else:
            rg = FakeResource(
                name="rgname",
                id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rgname"
            )

        return {
            'location': 'westus',
            'resource_group': rg,
        }


class GlobalFormRecognizerAccountPreparer(AzureMgmtPreparer):
    def __init__(self):
        super(GlobalFormRecognizerAccountPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )

    def create_resource(self, name, **kwargs):
        form_recognizer_account = FormRecognizerTest._FORM_RECOGNIZER_ACCOUNT

        return {
            'location': 'westus2',
            'resource_group': FormRecognizerTest._RESOURCE_GROUP,
            'form_recognizer_account': form_recognizer_account,
            'form_recognizer_account_key': FormRecognizerTest._FORM_RECOGNIZER_KEY,
        }


@pytest.fixture(scope="session")
def form_recognizer_account():
    test_case = AzureTestCase("__init__")
    rg_preparer = ResourceGroupPreparer(random_name_enabled=True, name_prefix='pycog')
    form_recognizer_preparer = CognitiveServicesAccountPreparer(random_name_enabled=True, kind="formrecognizer", name_prefix='pycog')

    try:
        rg_name, rg_kwargs = rg_preparer._prepare_create_resource(test_case)
        FormRecognizerTest._RESOURCE_GROUP = rg_kwargs['resource_group']
        try:
            form_recognizer_name, form_recognizer_kwargs = form_recognizer_preparer._prepare_create_resource(test_case, **rg_kwargs)
            FormRecognizerTest._FORM_RECOGNIZER_ACCOUNT = form_recognizer_kwargs['cognitiveservices_account']
            FormRecognizerTest._FORM_RECOGNIZER_KEY = form_recognizer_kwargs['cognitiveservices_account_key']
            yield
        finally:
            form_recognizer_preparer.remove_resource(
                form_recognizer_name,
                resource_group=rg_kwargs['resource_group']
            )
            FormRecognizerTest._FORM_RECOGNIZER_ACCOUNT = None
            FormRecognizerTest._FORM_RECOGNIZER_KEY = None
    finally:
        rg_preparer.remove_resource(rg_name)
        FormRecognizerTest._RESOURCE_GROUP = None
