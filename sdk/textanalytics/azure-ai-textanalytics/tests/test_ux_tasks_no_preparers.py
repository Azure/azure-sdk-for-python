# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Tasks listed here https://microsoft.sharepoint.com/teams/AzureDeveloperExperience/Shared%20Documents/Forms/AllItems.aspx?id=%2Fteams%2FAzureDeveloperExperience%2FShared%20Documents%2FUX%20Research%2F20%2D01%20Text%20Analytics%200120&p=true&originalPath=aHR0cHM6Ly9taWNyb3NvZnQuc2hhcmVwb2ludC5jb20vOmY6L3QvQXp1cmVEZXZlbG9wZXJFeHBlcmllbmNlL0VsV0tSQ0dUMjRsSml0NlM1eUt2UkNvQmtfTkczbUJ3NDB6YXd0end2ZzBSTWc_cnRpbWU9Y0hWWDFOelMyRWc
"""

def test_task_two():
    """
    Find words in the reviews that can be categorized as a person, location, or organization. Print the
    result found in text and it’s category, e.g. Kurt Russell is a Person.
    """
    import json
    import os
    from azure.core.pipeline.transport import HttpRequest
    from azure.identity import DefaultAzureCredential
    from azure.ai.textanalytics import TextAnalyticsClient

    client = TextAnalyticsClient(
        endpoint="https://python-textanalytics.cognitiveservices.azure.com/",
        credential=DefaultAzureCredential()
    )

    path_to_data = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "./data_inputs/task_2_data.json"
        )
    )

    with open(path_to_data) as file:
        documents = json.load(file)

    request = HttpRequest("POST", "/text/analytics/v3.1-preview.1/entities/recognition/general",
        json={
            "documents": documents
        }
    )

    response = client.send_request(request)
    response.raise_for_status()

    json_response = response.json()

    categories_we_want = ["Person", "Location", "Organization"]

    [
        print(f"'{entity['text']}' is a '{entity['category']}'")
        for doc in json_response['documents']
        for entity in doc['entities']
        if entity['category'] in categories_we_want
    ]


def test_task_3():
    """Find Person entities that may have entries in Wikipedia and print the url to their Wikipedia link.
    """
    import json
    import os
    from azure.core.pipeline.transport import HttpRequest
    from azure.identity import DefaultAzureCredential
    from azure.ai.textanalytics import TextAnalyticsClient

    client = TextAnalyticsClient(
        endpoint="https://python-textanalytics.cognitiveservices.azure.com/",
        credential=DefaultAzureCredential()
    )

    path_to_data = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "./data_inputs/task_2_data.json"
        )
    )

    with open(path_to_data) as file:
        documents = json.load(file)

    # get person entities

    request = HttpRequest("POST", "/text/analytics/v3.1-preview.1/entities/recognition/general",
        json={
            "documents": documents
        }
    )

    response = client.send_request(request)
    response.raise_for_status()
    person_entities = [
        entity["text"]
        for doc in response.json()['documents']
        for entity in doc['entities']
        if entity['category'] == "Person"
    ]

    # Get linked entities


    request = HttpRequest("POST", "/text/analytics/v3.1-preview.1/entities/linking",
        json={
            "documents": documents
        }
    )

    response = client.send_request(request)
    response.raise_for_status()

    json_response = response.json()

    [
        print(f"Person '{entity['name']}' has Wikipedia url'{entity['url']}'")
        for doc in json_response['documents']
        for entity in doc['entities']
        if entity['name'] in person_entities and entity['dataSource'] == "Wikipedia"
    ]

def test_task_4():
    """You are provided with a new dataset in JSON that includes multiple languages and is named [reviews_mixed.json].
    Use text analytics API to detect the language for each review. Then,
    print any Personal Identifiable Information found in the reviews.
    """
    import json
    import os
    from azure.core.pipeline.transport import HttpRequest
    from azure.identity import DefaultAzureCredential
    from azure.ai.textanalytics import TextAnalyticsClient

    client = TextAnalyticsClient(
        endpoint="https://python-textanalytics.cognitiveservices.azure.com/",
        credential=DefaultAzureCredential()
    )

    path_to_data = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "./data_inputs/task_4_data.json"
        )
    )

    with open(path_to_data) as file:
        documents = json.load(file)

    # Get languages

    request = HttpRequest("POST", "/text/analytics/v3.1-preview.1/languages",
        json={
            "documents": documents
        }
    )

    response = client.send_request(request)
    response.raise_for_status()

    json_response = response.json()


    languages = {
        doc['id']: doc['detectedLanguage']['name']
        for doc in json_response['documents']
    }

    # Get PII

    request = HttpRequest("POST", "/text/analytics/v3.1-preview.1/entities/recognition/pii",
        json={
            "documents": documents
        }
    )

    response = client.send_request(request)
    response.raise_for_status()

    json_response = response.json()

    piis = {
        doc['id']: [ (entity.get('text'), entity.get('category')) for entity in doc['entities']]
        for doc in response.json()['documents']
    }

    ## Know that languages and piis have the same ids and lengths
    for key in languages:
        language_str = f"Doc with id#{key} is in language '{languages[key]}' and has "
        if piis[key]:
            pii_str = ", ".join([f"'{entity[1]}' with value {entity[0]}" for entity in piis[key]])
            print(language_str + f"PII entit(ies): {pii_str}")
        else:
            print(language_str + "no PII entities")
