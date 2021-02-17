
# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import pytest
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.identity.aio import DefaultAzureCredential

@pytest.fixture()
def documents():
    documents = [
        """
        Microsoft was founded by Bill Gates and Paul Allen. I like the food Microsoft serves, it's very good.
        """,
        """
        最近由于工作压力太大，我们决定去富酒店度假。那儿的温泉实在太舒服了，我跟我丈夫都完全恢复了工作前的青春精神！加油！
        """,
        """
        My SSN is 859-98-0987
        """
    ]
    return [{"id": str(idx), "text": doc} for idx, doc in enumerate(documents)]

@pytest.fixture
async def client():
    async with DefaultAzureCredential() as credential:
        async with TextAnalyticsClient(endpoint="https://python-textanalytics.cognitiveservices.azure.com/", credential=credential) as client:
            yield client