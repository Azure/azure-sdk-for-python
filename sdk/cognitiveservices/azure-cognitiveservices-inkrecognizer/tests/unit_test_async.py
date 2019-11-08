#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import time
import asyncio
from unittest.mock import Mock
import pytest
from azure.cognitiveservices.inkrecognizer.aio import InkRecognizerClient


RAISE_ONLINE_TEST_ERRORS = False
URL = ""
CREDENTIAL = Mock(name="FakeCredential", get_token="token")


def online_test(func):
    def wrapper(*args, **kw):
        if URL == "" or isinstance(CREDENTIAL, Mock):
            if RAISE_ONLINE_TEST_ERRORS:
                raise ValueError("Please fill URL and CREDENTIAL before running online tests.")
            else:
                return
        return func(*args, **kw)
    return wrapper


class TestSendRequests:    
    @online_test
    @pytest.mark.asyncio
    async def test_recognize_ink_async(self):
        point = Mock(x=0, y=0)
        stroke = Mock(id=0, points=[point], language="python")
        ink_stroke_list = [stroke] * 3
        client = InkRecognizerClient(URL, CREDENTIAL)
        root = await client.recognize_ink(ink_stroke_list)
        assert root is not None