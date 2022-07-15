# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_custom_entities_async.py

DESCRIPTION:
    This sample demonstrates how to recognize custom entities in documents.
    Recognizing custom entities is also available as an action type through the begin_analyze_actions API.

    For information on regional support of custom features and how to train a model to
    recognize custom entities, see https://aka.ms/azsdk/textanalytics/customentityrecognition

USAGE:
    python sample_recognize_custom_entities_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key
    3) CUSTOM_ENTITIES_PROJECT_NAME - your Language Language Studio project name
    4) CUSTOM_ENTITIES_DEPLOYMENT_NAME - your Language deployed model name
"""


import os
import asyncio


async def sample_recognize_custom_entities_async():
    # [START recognize_custom_entities_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics.aio import TextAnalyticsClient

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]
    project_name = os.environ["CUSTOM_ENTITIES_PROJECT_NAME"]
    deployment_name = os.environ["CUSTOM_ENTITIES_DEPLOYMENT_NAME"]
    path_to_sample_document = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "..",
            "./text_samples/custom_entities_sample.txt",
        )
    )

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )

    with open(path_to_sample_document) as fd:
        document = [fd.read()]

    async with text_analytics_client:
        poller = await text_analytics_client.begin_recognize_custom_entities(
            document,
            project_name=project_name,
            deployment_name=deployment_name
        )

        document_results = await poller.result()

        async for custom_entities_result in document_results:
            if not custom_entities_result.is_error:
                for entity in custom_entities_result.entities:
                    print(
                        "Entity '{}' has category '{}' with confidence score of '{}'".format(
                            entity.text, entity.category, entity.confidence_score
                        )
                    )
            else:
                print("...Is an error with code '{}' and message '{}'".format(
                    custom_entities_result.code, custom_entities_result.message
                    )
                )
    # [END recognize_custom_entities_async]


async def main():
    await sample_recognize_custom_entities_async()


if __name__ == '__main__':
    asyncio.run(main())
