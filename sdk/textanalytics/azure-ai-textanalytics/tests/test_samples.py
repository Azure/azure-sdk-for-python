# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import sys
import pytest
import functools
from glob import glob
from subprocess import check_call
from testcase import TextAnalyticsTest, GlobalTextAnalyticsAccountPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from azure.ai.textanalytics import TextAnalyticsClient


# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)

samples_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "samples")
sample_files = list(
    filter(
        lambda x: os.path.basename(x) != "sample_authentication.py",  # Having some trouble getting the AAD auth to work without a custom subdomain associated with the resource
        [x for x in glob("%s/*.py" % samples_directory)]
    )
)


@pytest.fixture()
def text_analytics_test(text_analytics_account):
    return TextAnalyticsTest('__init__')


@pytest.fixture(params=[pytest.param(x, id=os.path.basename(x)) for x in sample_files])
def sample_file(request):
    return request.param


def test_sample(text_analytics_test, sample_file):
    azure_core_credentials = text_analytics_test.settings.get_azure_core_credentials()

    python_cmd = [sys.executable, sample_file]
    check_call(
        python_cmd,
        env={
            "AZURE_TEXT_ANALYTICS_ENDPOINT": TextAnalyticsTest._TEXT_ANALYTICS_ACCOUNT,
            "AZURE_TEXT_ANALYTICS_KEY": TextAnalyticsTest._TEXT_ANALYTICS_KEY,
            # "AZURE_TENANT_ID": azure_core_credentials._tenant_id,
            # "AZURE_CLIENT_ID": azure_core_credentials._client_id,
            # "AZURE_CLIENT_SECRET": azure_core_credentials._client_credential
        }
    )
