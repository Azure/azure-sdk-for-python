# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_multi_category_classify_async.py

DESCRIPTION:
    This sample demonstrates how to classify documents into multiple custom categories. Here we have a few
    movie plot summaries that must be categorized into movie genres like Sci-Fi, Horror, Comedy, Romance, etc.
    Classifying documents is available as an action type through the begin_analyze_actions API.

    To train a model to classify your documents, see TODO

USAGE:
    python sample_multi_category_classify_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
    3) AZURE_TEXT_ANALYTICS_PROJECT_NAME - your Text Analytics Language Studio project name
    4) AZURE_TEXT_ANALYTICS_DEPLOYMENT_NAME - your Text Analytics deployed model name
"""


import os
import asyncio


async def sample_classify_document_multi_categories_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics.aio import TextAnalyticsClient
    from azure.ai.textanalytics import MultiCategoryClassifyAction

    endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
    key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]
    project_name = os.environ["AZURE_TEXT_ANALYTICS_PROJECT_NAME"]
    deployed_model_name = os.environ["AZURE_TEXT_ANALYTICS_DEPLOYMENT_NAME"]

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )

    documents = [
        "In the not-too-distant future, Earth's dying sun spells the end for humanity. In a last-ditch effort to "
        "save the planet, a crew of eight men and women ventures into space with a device that could revive the "
        "star. However, an accident, a grave mistake and a distress beacon from a long-lost spaceship throw "
        "the crew and its desperate mission into a tailspin.",

        "Despite his family's generations-old ban on music, young Miguel dreams of becoming an accomplished "
        "musician like his idol Ernesto de la Cruz. Desperate to prove his talent, Miguel finds himself "
        "in the stunning and colorful Land of the Dead. After meeting a charming trickster named Héctor, "
        "the two new friends embark on an extraordinary journey to unlock the real story behind Miguel's "
        "family history"
    ]
    async with text_analytics_client:
        poller = await text_analytics_client.begin_analyze_actions(
            documents,
            actions=[
                MultiCategoryClassifyAction(
                    project_name=project_name,
                    deployment_name=deployed_model_name
                ),
            ],
        )

        pages = await poller.result()

        document_results = []
        async for page in pages:
            document_results.append(page)
    for doc, classification_results in zip(documents, document_results):
        for classification_result in classification_results:
            if not classification_result.is_error:
                classifications = classification_result.classifications
                print("The movie plot '{}' was classified as the following genres:\n".format(doc))
                for classification in classifications:
                    print("'{}' with confidence score {}.".format(
                        classification.category, classification.confidence_score
                    ))
            else:
                print("Movie plot '{}' has an error with code '{}' and message '{}'".format(
                    doc, classification_result.code, classification_result.message
                ))


async def main():
    await sample_classify_document_multi_categories_async()


if __name__ == '__main__':
    asyncio.run(main())
