# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import platform
import functools

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from testcase import TextAnalyticsPreparer
from testcase import TextAnalyticsTest
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.textanalytics.aio import TextAnalyticsClient

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
# the first one
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)

class TestEncoding(TextAnalyticsTest):
    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_emoji(self, **kwargs):
        client = kwargs.pop("client")
        result = await client.recognize_pii_entities(["👩 SSN: 859-98-0987"])
        assert result[0].entities[0].offset == 7

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_emoji_with_skin_tone_modifier(self, **kwargs):
        client = kwargs.pop("client")
        result = await client.recognize_pii_entities(["👩🏻 SSN: 859-98-0987"])
        assert result[0].entities[0].offset == 8

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_emoji_family(self, **kwargs):
        client = kwargs.pop("client")
        result = await client.recognize_pii_entities(["👩‍👩‍👧‍👧 SSN: 859-98-0987"])
        assert result[0].entities[0].offset == 13

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_emoji_family_with_skin_tone_modifier(self, **kwargs):
        client = kwargs.pop("client")
        result = await client.recognize_pii_entities(["👩🏻‍👩🏽‍👧🏾‍👦🏿 SSN: 859-98-0987"])
        assert result[0].entities[0].offset == 17

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_diacritics_nfc(self, **kwargs):
        client = kwargs.pop("client")
        result = await client.recognize_pii_entities(["año SSN: 859-98-0987"])
        assert result[0].entities[0].offset == 9

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_diacritics_nfd(self, **kwargs):
        client = kwargs.pop("client")
        result = await client.recognize_pii_entities(["año SSN: 859-98-0987"])
        assert result[0].entities[0].offset == 10

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_korean_nfc(self, **kwargs):
        client = kwargs.pop("client")
        result = await client.recognize_pii_entities(["아가 SSN: 859-98-0987"])
        assert result[0].entities[0].offset == 8

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_korean_nfd(self, **kwargs):
        client = kwargs.pop("client")
        result = await client.recognize_pii_entities(["아가 SSN: 859-98-0987"])
        assert result[0].entities[0].offset == 8

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_zalgo_text(self, **kwargs):
        client = kwargs.pop("client")
        result = await client.recognize_pii_entities(["ơ̵̧̧̢̳̘̘͕͔͕̭̟̙͎͈̞͔̈̇̒̃͋̇̅͛̋͛̎́͑̄̐̂̎͗͝m̵͍͉̗̄̏͌̂̑̽̕͝͠g̵̢̡̢̡̨̡̧̛͉̞̯̠̤̣͕̟̫̫̼̰͓̦͖̣̣͎̋͒̈́̓̒̈̍̌̓̅͑̒̓̅̅͒̿̏́͗̀̇͛̏̀̈́̀̊̾̀̔͜͠͝ͅ SSN: 859-98-0987"])


        assert result[0].entities[0].offset == 121
