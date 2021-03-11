# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
from azure.ai.textanalytics import TextAnalyticsApiVersion
from azure.ai.textanalytics.aio import TextAnalyticsClient
from testcase import TextAnalyticsTest, GlobalTextAnalyticsAccountPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)

class TestRecognizeEntities(TextAnalyticsTest):
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_default_api_version(self, client):
        assert "v3.1-preview.4" in client._client._client._base_url

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_0})
    def test_v3_0_api_version(self, client):
        assert "v3.0" in client._client._client._base_url

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1_PREVIEW})
    def test_v3_1_preview_api_version(self, client):
        assert "v3.1-preview.4" in client._client._client._base_url