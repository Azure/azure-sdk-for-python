# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_extract_key_phrases_vietnamese_async.py

DESCRIPTION:
    This sample demonstrates asynchronous key phrase extraction for Vietnamese documents.

USAGE:
    python sample_extract_key_phrases_vietnamese_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key.
"""

import asyncio


async def sample_extract_key_phrases_vietnamese_async() -> None:
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics.aio import TextAnalyticsClient

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]
    client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    articles = [
        {
            "id": "1",
            "language": "vi",
            "text": "Thành phố Đà Nẵng triển khai hệ thống giao thông thông minh để giảm ùn tắc.",
        },
        {
            "id": "2",
            "language": "vi",
            "text": "Doanh nghiệp đầu tư vào năng lượng tái tạo và mở rộng trung tâm dữ liệu.",
        },
    ]

    async with client:
        result = await client.extract_key_phrases(articles)

    for index, document in enumerate(result):
        if document.is_error:
            print(f"Error analyzing article {index + 1}: {document.error}")
        else:
            print(f"Key phrases in article {index + 1}: {', '.join(document.key_phrases)}")


async def main() -> None:
    await sample_extract_key_phrases_vietnamese_async()


if __name__ == "__main__":
    asyncio.run(main())