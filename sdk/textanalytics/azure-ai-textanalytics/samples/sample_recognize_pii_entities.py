# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_pii_entities.py

DESCRIPTION:
    This sample demonstrates how to recognize personally identifiable information in a batch of documents.
    The endpoint recognize_pii_entities is only available for API version v3.1 and up.

    In this sample, we will be working for a company that handles loan payments. To follow privacy guidelines,
    we need to redact all of our information before we make it public.

USAGE:
    python sample_recognize_pii_entities.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key
"""

import os


def sample_recognize_pii_entities() -> None:
    print(
        "In this sample we will be going through our customer's loan payment information and redacting "
        "all PII (personally identifiable information) before storing this information on our public website. "
        "I'm also looking to explicitly extract the SSN information, so I can update my database with SSNs for "
        "our customers"
    )
    # [START recognize_pii_entities]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import TextAnalyticsClient

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    documents = [
        """Parker Doe has repaid all of their loans as of 2020-04-25.
        Their SSN is 859-98-0987. To contact them, use their phone number
        555-555-5555. They are originally from Brazil and have Brazilian CPF number 998.214.865-68"""
    ]

    result = text_analytics_client.recognize_pii_entities(documents)
    docs = [doc for doc in result if not doc.is_error]

    print(
        "Let's compare the original document with the documents after redaction. "
        "I also want to comb through all of the entities that got redacted"
    )
    for idx, doc in enumerate(docs):
        print(f"Document text: {documents[idx]}")
        print(f"Redacted document text: {doc.redacted_text}")
        for entity in doc.entities:
            print("...Entity '{}' with category '{}' got redacted".format(
                entity.text, entity.category
            ))

    # [END recognize_pii_entities]
    print("All of the information that I expect to be redacted is!")

    print(
        "Now I want to explicitly extract SSN information to add to my user SSN database. "
        "I also want to be fairly confident that what I'm storing is an SSN, so let's also "
        "ensure that we're > 60% positive the entity is a SSN"
    )
    social_security_numbers = []
    for doc in docs:
        for entity in doc.entities:
            if entity.category == 'USSocialSecurityNumber' and entity.confidence_score >= 0.6:
                social_security_numbers.append(entity.text)

    print("We have extracted the following SSNs as well: '{}'".format(
        "', '".join(social_security_numbers)
    ))


if __name__ == '__main__':
    sample_recognize_pii_entities()
