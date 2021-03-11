# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_batch_actions.py

DESCRIPTION:
    This sample demonstrates how to submit a collection of text documents for analysis, which consists of a variety
    of text analysis actions, such as Entity Recognition, PII Entity Recognition,
    or Key Phrase Extraction.  The response will contain results from each of the individual actions specified in the request.

USAGE:
    python sample_analyze_batch_actions.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""


import os


class AnalyzeSample(object):

    def analyze(self):
        # [START analyze]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import (
            TextAnalyticsClient,
            RecognizeEntitiesAction,
            RecognizeLinkedEntitiesAction,
            RecognizePiiEntitiesAction,
            ExtractKeyPhrasesAction,
            PiiEntityDomainType,
        )

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )

        documents = [
            "We went to Contoso Steakhouse located at midtown NYC last week for a dinner party, and we adore the spot! \
            They provide marvelous food and they have a great menu. The chief cook happens to be the owner (I think his name is John Doe) \
            and he is super nice, coming out of the kitchen and greeted us all. We enjoyed very much dining in the place! \
            The Sirloin steak I ordered was tender and juicy, and the place was impeccably clean. You can even pre-order from their \
            online menu at www.contososteakhouse.com, call 312-555-0176 or send email to order@contososteakhouse.com! \
            The only complaint I have is the food didn't come fast enough. Overall I highly recommend it!"
        ]

        poller = text_analytics_client.begin_analyze_batch_actions(
            documents,
            display_name="Sample Text Analysis",
            actions=[
                RecognizeEntitiesAction(),
                RecognizePiiEntitiesAction(domain_filter=PiiEntityDomainType.PROTECTED_HEALTH_INFORMATION),
                ExtractKeyPhrasesAction(),
                RecognizeLinkedEntitiesAction()
            ],
        )

        result = poller.result()
        action_results = [action_result for action_result in list(result) if not action_result.is_error]

        first_action_result = action_results[0]
        print("Results of Entities Recognition action:")
        docs = [doc for doc in first_action_result.document_results if not doc.is_error]

        for idx, doc in enumerate(docs):
            print("\nDocument text: {}".format(documents[idx]))
            for entity in doc.entities:
                print("Entity: {}".format(entity.text))
                print("...Category: {}".format(entity.category))
                print("...Confidence Score: {}".format(entity.confidence_score))
                print("...Offset: {}".format(entity.offset))
                print("...Length: {}".format(entity.length))
            print("------------------------------------------")

        second_action_result = action_results[1]
        print("Results of PII Entities Recognition action:")
        docs = [doc for doc in second_action_result.document_results if not doc.is_error]

        for idx, doc in enumerate(docs):
            print("Document text: {}".format(documents[idx]))
            print("Document text with redactions: {}".format(doc.redacted_text))
            for entity in doc.entities:
                print("Entity: {}".format(entity.text))
                print("...Category: {}".format(entity.category))
                print("...Confidence Score: {}\n".format(entity.confidence_score))
                print("...Offset: {}".format(entity.offset))
                print("...Length: {}".format(entity.length))
            print("------------------------------------------")

        third_action_result = action_results[2]
        print("Results of Key Phrase Extraction action:")
        docs = [doc for doc in third_action_result.document_results if not doc.is_error]

        for idx, doc in enumerate(docs):
            print("Document text: {}\n".format(documents[idx]))
            print("Key Phrases: {}\n".format(doc.key_phrases))
            print("------------------------------------------")

        fourth_action_result = action_results[3]
        print("Results of Linked Entities Recognition action:")
        docs = [doc for doc in fourth_action_result.document_results if not doc.is_error]

        for idx, doc in enumerate(docs):
            print("Document text: {}\n".format(documents[idx]))
            for linked_entity in doc.entities:
                print("Entity name: {}".format(linked_entity.name))
                print("...Data source: {}".format(linked_entity.data_source))
                print("...Data source language: {}".format(linked_entity.language))
                print("...Data source entity ID: {}".format(linked_entity.data_source_entity_id))
                print("...Data source URL: {}".format(linked_entity.url))
                print("...Document matches:")
                for match in linked_entity.matches:
                    print("......Match text: {}".format(match.text))
                    print(".........Confidence Score: {}".format(match.confidence_score))
                    print(".........Offset: {}".format(match.offset))
                    print(".........Length: {}".format(match.length))
            print("------------------------------------------")

        # [END analyze]


if __name__ == "__main__":
    sample = AnalyzeSample()
    sample.analyze()
