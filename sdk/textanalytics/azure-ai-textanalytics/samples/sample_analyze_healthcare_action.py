# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_healthcare_action.py

DESCRIPTION:
    This sample demonstrates how to submit a collection of text documents for analysis, which uses the
    AnalyzeHealthcareEntitiesAction and RecognizePiiEntitiesAction to recognize healthcare entities,
    along with any PII entities.
    The response will contain results from each of the individual actions specified in the request.

USAGE:
    python sample_analyze_healthcare_action.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key
"""


import os


def sample_analyze_healthcare_action() -> None:
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import (
        TextAnalyticsClient,
        AnalyzeHealthcareEntitiesAction,
        RecognizePiiEntitiesAction,
    )

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )

    documents = [
        """
        Patient needs to take 100 mg of ibuprofen, and 3 mg of potassium. Also needs to take
        10 mg of Zocor.
        """,
        """
        Patient needs to take 50 mg of ibuprofen, and 2 mg of Coumadin.
        """
    ]

    poller = text_analytics_client.begin_analyze_actions(
        documents,
        display_name="Sample Text Analysis",
        actions=[
            AnalyzeHealthcareEntitiesAction(),
            RecognizePiiEntitiesAction(domain_filter="phi"),
        ],
    )

    document_results = poller.result()
    for doc, action_results in zip(documents, document_results):
        print(f"\nDocument text: {doc}")
        for result in action_results:
            if result.kind == "Healthcare":
                print("...Results of Analyze Healthcare Entities Action:")
                for entity in result.entities:
                    print(f"Entity: {entity.text}")
                    print(f"...Normalized Text: {entity.normalized_text}")
                    print(f"...Category: {entity.category}")
                    print(f"...Subcategory: {entity.subcategory}")
                    print(f"...Offset: {entity.offset}")
                    print(f"...Confidence score: {entity.confidence_score}")
                    if entity.data_sources is not None:
                        print("...Data Sources:")
                        for data_source in entity.data_sources:
                            print(f"......Entity ID: {data_source.entity_id}")
                            print(f"......Name: {data_source.name}")
                    if entity.assertion is not None:
                        print("...Assertion:")
                        print(f"......Conditionality: {entity.assertion.conditionality}")
                        print(f"......Certainty: {entity.assertion.certainty}")
                        print(f"......Association: {entity.assertion.association}")
                for relation in result.entity_relations:
                    print(f"Relation of type: {relation.relation_type} has the following roles")
                    for role in relation.roles:
                        print(f"...Role '{role.name}' with entity '{role.entity.text}'")

            elif result.kind == "PiiEntityRecognition":
                print("Results of Recognize PII Entities action:")
                for entity in result.entities:
                    print(f"......Entity: {entity.text}")
                    print(f".........Category: {entity.category}")
                    print(f".........Confidence Score: {entity.confidence_score}")

            elif result.kind == "DocumentError":
                print(f"...Is an error with code '{result.code}' and message '{result.message}'")

            print("------------------------------------------")


if __name__ == "__main__":
    sample_analyze_healthcare_action()
