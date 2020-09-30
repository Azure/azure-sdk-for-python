# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_text.py

DESCRIPTION:
    This sample demonstrates how to submit a collection of text documents for analysis, which consists of a variety
    of text analysis tasks, such as Entity Recognition, PII Entity Recognition, Entity Linking, Sentiment Analysis,
    or Key Phrase Extraction.  The response will contain results from each of the individual tasks specified in the request.

USAGE:
    python sample_analyze_text.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""


import os


class AnalyzeTextSample(object):

    def analyze_text(self):
        # [START analyze_text]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient, \
            EntitiesRecognitionTask, \
            PiiEntitiesRecognitionTask, \
            EntityLinkingTask, \
            KeyPhraseExtractionTask, \
            SentimentAnalysisTask

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key),
            api_version="v3.2-preview.1"
        )

        documents = [
            "I had a wonderful trip to Seattle last week.",
            "I'm flying to NYC tomorrow. See you there."
        ]

        poller = text_analytics_client.begin_analyze_text(
            documents,
            display_name="Sample Text Analysis",
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            entity_linking_tasks=[EntityLinkingTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            sentiment_analysis_tasks=[SentimentAnalysisTask()]
        )

        result = poller.result()

        for page in result:
            for task in page.entities_recognition_tasks:
                print("Results of task '{}':".format(task.name))
                
                docs = [doc for doc in task.results.documents if not doc.is_error]
                for idx, doc in enumerate(docs):
                    print("\nDocument text: {}".format(documents[idx]))
                    for entity in doc.entities:
                        print("Entity: {}".format(entity.text))
                        print("...Category: {}".format(entity.category))
                        print("...Confidence Score: {}".format(entity.confidence_score))
                        print("...Offset: {}".format(entity.offset))
                        print("...Length: {}".format(entity.length))
                    print("------------------------------------------")

            for task in page.pii_entities_recognition_tasks:
                print("Results of task '{}':".format(task.name))

                docs = [doc for doc in task.results.documents if not doc.is_error]
                for idx, doc in enumerate(docs):
                    print("Document text: {}".format(documents[idx]))
                    for entity in doc.entities:
                        print("Entity: {}".format(entity.text))
                        print("Category: {}".format(entity.category))
                        print("Confidence Score: {}\n".format(entity.confidence_score))
                    print("------------------------------------------")


            for task in page.entity_linking_tasks:
                print("Results of task '{}':".format(task.name))

                docs = [doc for doc in task.results.documents if not doc.is_error]
                for idx, doc in enumerate(docs):
                    print("Document text: {}\n".format(documents[idx]))
                    for entity in doc.entities:
                        print("Entity: {}".format(entity.name))
                        print("...URL: {}".format(entity.url))
                        print("...Data Source: {}".format(entity.data_source))
                        print("...Entity matches:")
                        for match in entity.matches:
                            print("......Entity match text: {}".format(match.text))
                            print("......Confidence Score: {}".format(match.confidence_score))
                            print("......Offset: {}".format(match.offset))
                            print("......Length: {}".format(match.length))
                    print("------------------------------------------")

            for task in page.keyphrase_extraction_tasks:
                print("Results of task '{}':".format(task.name))

                docs = [doc for doc in task.results.documents if not doc.is_error]
                for idx, doc in enumerate(docs):
                    print("Document text: {}\n".format(documents[idx]))
                    print("Key Phrases: {}\n".format(doc.key_phrases))
                    print("------------------------------------------")

            for task in page.sentiment_analysis_tasks:
                print("Results of task '{}':".format(task.name))

                docs = [doc for doc in task.results.documents if not doc.is_error]
                for idx, doc in enumerate(docs):
                    print("Document text: {}".format(documents[idx]))
                    print("Overall sentiment: {}".format(doc.sentiment))
                    print("Overall confidence scores: positive={}; neutral={}; negative={} \n".format(
                        doc.confidence_scores.positive,
                        doc.confidence_scores.neutral,
                        doc.confidence_scores.negative,
                    ))
                    for sentence in doc.sentences:
                        print("Sentence '{}' has sentiment: {}".format(sentence.text, sentence.sentiment))
                        print("...Sentence is {} characters from the start of the document and is {} characters long".format(
                            sentence.offset, sentence.length
                        ))
                        print("...Sentence confidence scores: positive={}; neutral={}; negative={}".format(
                            sentence.confidence_scores.positive,
                            sentence.confidence_scores.neutral,
                            sentence.confidence_scores.negative,
                        ))
                    print("------------------------------------------")

        # [END analyze_text]


if __name__ == "__main__":
    sample = AnalyzeTextSample()
    sample.analyze_text()