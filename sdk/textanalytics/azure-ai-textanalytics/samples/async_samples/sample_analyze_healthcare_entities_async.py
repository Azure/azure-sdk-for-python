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
            "We start out with a list of prescription documents. "
            "To simplify matters, we will assume all dosages are in units of mg."
        )

        # [START analyze_healthcare_entities_async]
        import re
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics.aio import TextAnalyticsClient
        from collections import defaultdict

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

            print(
                "In order to find the total dosage for every mentioned medication, "
                "let's create a dict, mapping medication name -> total dosage. "
            )

            medication_to_dosage = defaultdict(int)

            print(
                "We will start off by extracting all of the dosage entities."
            )

            dosage_entities = [
                entity
                for doc in docs
                for entity in doc.entities
                if entity.category == "Dosage"
            ]

            print(
                "Now we traverse the related entities of each dosage entity. "
                "We are looking for entities that are related by 'DosageOfMedication'. "
                "After that, we're done!"
            )
            for dosage in dosage_entities:
                dosage_value = int(re.findall(r"\d+", dosage.text)[0]) # we find the numbers in the dosage
                for related_entity, relation_type in dosage.related_entities.items():
                    if relation_type == "DosageOfMedication":
                        medication_to_dosage[related_entity.text] += dosage_value

            [
                print("We have fulfilled '{}' total mg of '{}'".format(
                    dosage, medication
                ))
                for medication, dosage in medication_to_dosage.items()
            ]
        # [END analyze_healthcare_entities_async]

async def main():
    sample = AnalyzeHealthcareEntitiesSampleAsync()
    await sample.analyze_healthcare_entities_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
