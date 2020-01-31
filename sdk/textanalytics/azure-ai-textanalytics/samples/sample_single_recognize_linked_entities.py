# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_single_recognize_linked_entities.py

DESCRIPTION:
    This sample demonstrates how to recognize entities in a single string
    and returns links to the entities from a well-known knowledge base.

    This module-level, single method is meant to be used as an introduction
    for new users of the text analytics service. For optimum use of the service,
    use the methods that support batching documents.

USAGE:
    python sample_single_recognize_linked_entities.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key

OUTPUT:
    Entity: Easter Island
    Url: https://en.wikipedia.org/wiki/Easter_Island
    Data Source: Wikipedia

    Where this entity appears in the text:
    Match 1: Easter Island
    Score: 0.272
    Offset: 0
    Length: 13

    Match 2: Rapa Nui
    Score: 0.054
    Offset: 97
    Length: 8

    Entity: Polynesia
    Url: https://en.wikipedia.org/wiki/Polynesia
    Data Source: Wikipedia

    Where this entity appears in the text:
    Match 1: Polynesia
    Score: 0.163
    Offset: 67
    Length: 9

    Entity: Chile
    Url: https://en.wikipedia.org/wiki/Chile
    Data Source: Wikipedia

    Where this entity appears in the text:
    Match 1: Chilean
    Score: 0.045
    Offset: 17
    Length: 7

"""

import os


class SingleRecognizeLinkedEntitiesSample(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    def recognize_linked_entities(self):
        # [START single_recognize_linked_entities]
        from azure.ai.textanalytics import single_recognize_linked_entities, TextAnalyticsApiKeyCredential

        text = "Easter Island, a Chilean territory, is a remote volcanic island in Polynesia. " \
               "Its native name is Rapa Nui."

        result = single_recognize_linked_entities(
            endpoint=self.endpoint,
            credential=TextAnalyticsApiKeyCredential(self.key),
            input_text=text,
            language="en"
        )

        for entity in result.entities:
            print("Entity: {}".format(entity.name))
            print("Url: {}".format(entity.url))
            print("Data Source: {}\n".format(entity.data_source))
            print("Where this entity appears in the text:")
            for idx, match in enumerate(entity.matches):
                print("Match {}: {}".format(idx+1, match.text))
                print("Score: {0:.3f}".format(match.score))
                print("Offset: {}".format(match.offset))
                print("Length: {}\n".format(match.length))
        # [END single_recognize_linked_entities]


if __name__ == '__main__':
    sample = SingleRecognizeLinkedEntitiesSample()
    sample.recognize_linked_entities()
