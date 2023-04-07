# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example showing how to use httpx as the transport when using http based client libraries
"""

import asyncio


async def sample_abstractive_summarization_async() -> None:
    # [START abstractive_summary_async]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics.aio import TextAnalyticsClient
    from azure.core.experimental.transport import AsyncHttpXTransport

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
        transport=AsyncHttpXTransport(),
    )

    document = ["This is an example document."]

    async with text_analytics_client:
        poller = await text_analytics_client.begin_abstractive_summary(document)
        abstractive_summary_results = await poller.result()
        async for result in abstractive_summary_results:
            if result.kind == "AbstractiveSummarization":
                print("Summaries abstracted:")
                [print(f"{summary.text}\n") for summary in result.summaries]
            elif result.is_error is True:
                print("...Is an error with code '{}' and message '{}'".format(result.error.code, result.error.message))
    # [END abstractive_summary_async]


async def main():
    await sample_abstractive_summarization_async()


if __name__ == "__main__":
    asyncio.run(main())
