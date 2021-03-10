# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_healthcare_entities_async.py

DESCRIPTION:
    This sample demonstrates how to detect healthcare entities in a batch of documents.

    In this sample we will be a newly-hired engineer working in a pharmacy. We are going to
    comb through all of the prescriptions our pharmacy has fulfilled so we can catalog how
    much inventory we have.

    As a usage note: healthcare is currently in gated preview. Your subscription needs to
    be allow-listed before you can use this endpoint. More information about that here:
    https://aka.ms/text-analytics-health-request-access

USAGE:
    python sample_analyze_healthcare_entities_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""


import os
import asyncio


class AnalyzeHealthcareEntitiesSampleAsync(object):

    async def analyze_healthcare_entities_async(self):

        print(
            "In this sample we will be combing through the prescriptions our pharmacy has fulfilled "
            "so we can catalog how much inventory we have"
        )
        print(
            "We start out with a list of prescription documents."
        )

        # [START analyze_healthcare_entities_async]
        import os
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import HealthcareEntityRelationType, HealthcareEntityRelationRoleType
        from azure.ai.textanalytics.aio import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

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

        async with text_analytics_client:
            poller = await text_analytics_client.begin_analyze_healthcare_entities(documents)
            result = await poller.result()
            docs = [doc async for doc in result if not doc.is_error]

        print("Let's first visualize the outputted healthcare result:")
        for idx, doc in enumerate(docs):
            for entity in doc.entities:
                print("Entity: {}".format(entity.text))
                print("...Normalized Text: {}".format(entity.normalized_text))
                print("...Category: {}".format(entity.category))
                print("...Subcategory: {}".format(entity.subcategory))
                print("...Offset: {}".format(entity.offset))
                print("...Confidence score: {}".format(entity.confidence_score))
                if entity.data_sources is not None:
                    print("...Data Sources:")
                    for data_source in entity.data_sources:
                        print("......Entity ID: {}".format(data_source.entity_id))
                        print("......Name: {}".format(data_source.name))
                if entity.assertion is not None:
                    print("...Assertion:")
                    print("......Conditionality: {}".format(entity.assertion.conditionality))
                    print("......Certainty: {}".format(entity.assertion.certainty))
                    print("......Association: {}".format(entity.assertion.association))
            for relation in doc.entity_relations:
                print("Relation of type: {} has the following roles".format(relation.relation_type))
                for role in relation.roles:
                    print("...Role '{}' with entity '{}'".format(role.name, role.entity.text))
            print("------------------------------------------")

        print("Now, let's get all of medication dosage relations from the documents")
        dosage_of_medication_relations = [
            entity_relation
            for doc in docs
            for entity_relation in doc.entity_relations if entity_relation.relation_type == HealthcareEntityRelationType.DOSAGE_OF_MEDICATION
        ]
        # [END analyze_healthcare_entities_async]

        print(
            "Now, I will create a dictionary of medication to total dosage. "
            "I will use a regex to extract the dosage amount. For simplicity sake, I will assume "
            "all dosages are represented with numbers and have mg unit."
        )
        import re
        from collections import defaultdict

        medication_to_dosage = defaultdict(int)

        for relation in dosage_of_medication_relations:
            # The DosageOfMedication relation should only contain the dosage and medication roles

            dosage_role = next(filter(lambda x: x.name == HealthcareEntityRelationRoleType.DOSAGE, relation.roles))
            medication_role = next(filter(lambda x: x.name == HealthcareEntityRelationRoleType.MEDICATION, relation.roles))

            try:
                dosage_value = int(re.findall(r"\d+", dosage_role.entity.text)[0]) # we find the numbers in the dosage
                medication_to_dosage[medication_role.entity.text] += dosage_value
            except StopIteration:
                # Error handling for if there's no dosage in numbers.
                pass

        [
            print("We have fulfilled '{}' total mg of '{}'".format(
                dosage, medication
            ))
            for medication, dosage in medication_to_dosage.items()
        ]

async def main():
    sample = AnalyzeHealthcareEntitiesSampleAsync()
    await sample.analyze_healthcare_entities_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
