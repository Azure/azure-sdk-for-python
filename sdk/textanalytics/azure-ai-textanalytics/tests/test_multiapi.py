# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiVersion
from testcase import TextAnalyticsTest, TextAnalyticsPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from azure.ai.textanalytics._version import DEFAULT_API_VERSION

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)

class TestMultiApi(TextAnalyticsTest):
    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    def test_default_api_version(self, **kwargs):
        client = kwargs.pop("client")
        assert DEFAULT_API_VERSION in client._api_version  # api_version is in query now, not in base_url

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_0})
    def test_v3_0_api_version(self, **kwargs):
        client = kwargs.pop("client")
        assert "v3.0" in client._client._client._base_url

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    def test_v3_1_api_version(self, **kwargs):
        client = kwargs.pop("client")
        assert "v3.1" in client._client._client._base_url
