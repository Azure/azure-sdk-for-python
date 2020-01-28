# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_linked_entities.py

DESCRIPTION:
    This sample demonstrates how to detect linked entities in a batch of documents.
    Each entity found in the document will have a link associated with it from a
    data source.

USAGE:
    python sample_recognize_linked_entities.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key

OUTPUT:
    Document text: Microsoft moved its headquarters to Bellevue, Washington in January 1979.

    Entity: Bellevue, Washington
    Url: https://en.wikipedia.org/wiki/Bellevue,_Washington
    Data Source: Wikipedia
    Score: 0.698
    Offset: 36
    Length: 20

    Entity: Microsoft
    Url: https://en.wikipedia.org/wiki/Microsoft
    Data Source: Wikipedia
    Score: 0.159
    Offset: 0
    Length: 9

    Entity: January
    Url: https://en.wikipedia.org/wiki/January
    Data Source: Wikipedia
    Score: 0.007
    Offset: 60
    Length: 7

    ------------------------------------------
    Document text: Steve Ballmer stepped down as CEO of Microsoft and was succeeded by Satya Nadella.

    Entity: Steve Ballmer
    Url: https://en.wikipedia.org/wiki/Steve_Ballmer
    Data Source: Wikipedia
    Score: 0.672
    Offset: 0
    Length: 13

    Entity: Satya Nadella
    Url: https://en.wikipedia.org/wiki/Satya_Nadella
    Data Source: Wikipedia
    Score: 0.681
    Offset: 68
    Length: 13

    Entity: Microsoft
    Url: https://en.wikipedia.org/wiki/Microsoft
    Data Source: Wikipedia
    Score: 0.164
    Offset: 37
    Length: 9

    Entity: Chief executive officer
    Url: https://en.wikipedia.org/wiki/Chief_executive_officer
    Data Source: Wikipedia
    Score: 0.074
    Offset: 30
    Length: 3

    ------------------------------------------
    Document text: Microsoft superó a Apple Inc. como la compañía más valiosa que cotiza en bolsa en el mundo.

    Entity: Apple Inc.
    Url: https://en.wikipedia.org/wiki/Apple_Inc.
    Data Source: Wikipedia
    Score: 0.677
    Offset: 19
    Length: 10

    Entity: Microsoft
    Url: https://en.wikipedia.org/wiki/Microsoft
    Data Source: Wikipedia
    Score: 0.132
    Offset: 0
    Length: 9

    ------------------------------------------

"""

import os


class RecognizeLinkedEntitiesSample(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    def recognize_linked_entities(self):
        # [START batch_recognize_linked_entities]
        from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsAPIKeyCredential
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=TextAnalyticsAPIKeyCredential(self.key))
        documents = [
            "Microsoft moved its headquarters to Bellevue, Washington in January 1979.",
            "Steve Ballmer stepped down as CEO of Microsoft and was succeeded by Satya Nadella.",
            "Microsoft superó a Apple Inc. como la compañía más valiosa que cotiza en bolsa en el mundo.",
        ]

        result = text_analytics_client.recognize_linked_entities(documents)
        docs = [doc for doc in result if not doc.is_error]

        for idx, doc in enumerate(docs):
            print("Document text: {}\n".format(documents[idx]))
            for entity in doc.entities:
                print("Entity: {}".format(entity.name))
                print("Url: {}".format(entity.url))
                print("Data Source: {}".format(entity.data_source))
                for match in entity.matches:
                    print("Score: {0:.3f}".format(match.score))
                    print("Offset: {}".format(match.offset))
                    print("Length: {}\n".format(match.length))
            print("------------------------------------------")
        # [END batch_recognize_linked_entities]

    def alternative_scenario_recognize_linked_entities(self):
        """This sample demonstrates how to retrieve batch statistics, the
        model version used, and the raw response returned from the service.

        It additionally shows an alternative way to pass in the input documents
        using a list[TextDocumentInput] and supplying your own IDs and language hints along
        with the text.
        """
        from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsAPIKeyCredential
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=TextAnalyticsAPIKeyCredential(self.key))

        documents = [
            {"id": "0", "language": "en", "text": "Microsoft moved its headquarters to Bellevue, Washington in January 1979."},
            {"id": "1", "language": "en", "text": "Steve Ballmer stepped down as CEO of Microsoft and was succeeded by Satya Nadella."},
            {"id": "2", "language": "es", "text": "Microsoft superó a Apple Inc. como la compañía más valiosa que cotiza en bolsa en el mundo."},
        ]

        extras = []

        def callback(resp):
            extras.append(resp.statistics)
            extras.append(resp.model_version)
            extras.append(resp.raw_response)

        result = text_analytics_client.recognize_linked_entities(
            documents,
            show_stats=True,
            model_version="latest",
            response_hook=callback
        )


if __name__ == '__main__':
    sample = RecognizeLinkedEntitiesSample()
    sample.recognize_linked_entities()
    sample.alternative_scenario_recognize_linked_entities()
