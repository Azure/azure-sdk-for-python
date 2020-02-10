# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_pii_entities.py

DESCRIPTION:
    This sample demonstrates how to recognize personally identifiable information in a batch of documents.

USAGE:
    python sample_recognize_pii_entities.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key
"""

import os


class RecognizePiiEntitiesSample(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    def recognize_pii_entities(self):
        # [START batch_recognize_pii_entities]
        from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiKeyCredential
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=TextAnalyticsApiKeyCredential(self.key))
        documents = [
            "The employee's SSN is 555-55-5555.",
            "Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check.",
            "Is 998.214.865-68 your Brazilian CPF number?"
        ]

        result = text_analytics_client.recognize_pii_entities(documents)
        docs = [doc for doc in result if not doc.is_error]

        for idx, doc in enumerate(docs):
            print("Document text: {}".format(documents[idx]))
            for entity in doc.entities:
                print("Entity: {}".format(entity.text))
                print("Category: {}".format(entity.category))
                print("Confidence Score: {}\n".format(entity.score))
        # [END batch_recognize_pii_entities]

    def alternative_scenario_recognize_pii_entities(self):
        """This sample demonstrates how to retrieve batch statistics, the
        model version used, and the raw response returned from the service.

        It additionally shows an alternative way to pass in the input documents
        using a list[TextDocumentInput] and supplying your own IDs and language hints along
        with the text.
        """
        from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiKeyCredential
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=TextAnalyticsApiKeyCredential(self.key))

        documents = [
            {"id": "0", "language": "en", "text": "The employee's SSN is 555-55-5555."},
            {"id": "1", "language": "en", "text": "Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check."},
            {"id": "2", "language": "en", "text": "Is 998.214.865-68 your Brazilian CPF number?"}
        ]

        extras = []

        def callback(resp):
            extras.append(resp.statistics)
            extras.append(resp.model_version)
            extras.append(resp.raw_response)

        result = text_analytics_client.recognize_pii_entities(
            documents,
            show_stats=True,
            model_version="latest",
            response_hook=callback
        )


if __name__ == '__main__':
    sample = RecognizePiiEntitiesSample()
    sample.recognize_pii_entities()
    sample.alternative_scenario_recognize_pii_entities()
