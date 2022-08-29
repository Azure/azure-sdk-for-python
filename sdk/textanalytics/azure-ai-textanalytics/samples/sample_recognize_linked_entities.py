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

    In this sample, we are students conducting research for a class project. We want to extract
    Wikipedia articles for all of the entries listed in our documents, so we can have all possible
    links extracted out of our research documents.

USAGE:
    python sample_recognize_linked_entities.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key
"""

import os



def sample_recognize_linked_entities() -> None:
    print(
        "In this sample, we are students conducting research for a class project. We will extract "
        "links to Wikipedia articles for all entities listed in our research documents, so we have "
        "all of the necessary information for research purposes."
    )
    # [START recognize_linked_entities]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import TextAnalyticsClient

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]

    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    documents = [
        """
        Microsoft was founded by Bill Gates with some friends he met at Harvard. One of his friends,
        Steve Ballmer, eventually became CEO after Bill Gates as well. Steve Ballmer eventually stepped
        down as CEO of Microsoft, and was succeeded by Satya Nadella.
        Microsoft originally moved its headquarters to Bellevue, Washington in January 1979, but is now
        headquartered in Redmond.
        """
    ]

    result = text_analytics_client.recognize_linked_entities(documents)
    docs = [doc for doc in result if not doc.is_error]

    print(
        "Let's map each entity to it's Wikipedia article. I also want to see how many times each "
        "entity is mentioned in a document\n\n"
    )
    entity_to_url = {}
    for doc in docs:
        for entity in doc.entities:
            print("Entity '{}' has been mentioned '{}' time(s)".format(
                entity.name, len(entity.matches)
            ))
            if entity.data_source == "Wikipedia":
                entity_to_url[entity.name] = entity.url
    # [END recognize_linked_entities]

    print("\nNow let's see all of the Wikipedia articles we've extracted from our research documents")
    for entity, url in entity_to_url.items():
        print("Link to Wikipedia article for '{}': {}".format(
                entity, url
        ))


if __name__ == '__main__':
    sample_recognize_linked_entities()
