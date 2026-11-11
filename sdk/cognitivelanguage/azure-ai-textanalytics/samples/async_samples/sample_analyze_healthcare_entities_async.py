# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_analyze_healthcare_entities_async.py

DESCRIPTION:
    This sample demonstrates how to run a **healthcare** action over text (async LRO).

USAGE:
    python sample_analyze_healthcare_entities_async.py

REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_TEXT_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET

NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_TEXT_ENDPOINT
      - AZURE_TEXT_KEY
"""

# [START analyze_healthcare_entities_async]
import os
import asyncio

from azure.identity.aio import DefaultAzureCredential
from azure.ai.textanalytics.aio import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    AnalyzeTextOperationAction,
    HealthcareLROTask,
    HealthcareLROResult,
)


async def sample_analyze_healthcare_entities_async():
    # get settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    async with TextAnalysisClient(endpoint, credential=credential) as client:
        # Build input
        text_a = "Prescribed 100mg ibuprofen, taken twice daily."

        text_input = MultiLanguageTextInput(
            multi_language_inputs=[
                MultiLanguageInput(id="A", text=text_a, language="en"),
            ]
        )

        actions: list[AnalyzeTextOperationAction] = [
            HealthcareLROTask(name="Healthcare Operation"),
        ]

        # Start long-running operation (async) – poller returns AsyncItemPaged[TextActions]
        poller = await client.begin_analyze_text_job(
            text_input=text_input,
            actions=actions,
        )

        job_state = await poller.result()
        print(f"Job ID: {job_state.job_id}")
        print(f"Status: {job_state.status}")

        if job_state.actions:
            for op_result in job_state.actions.items_property or []:
                if isinstance(op_result, HealthcareLROResult):
                    print(f"\nAction Name: {op_result.task_name}")
                    print(f"Action Status: {op_result.status}")
                    print(f"Kind: {op_result.kind}")

                    hc_result = op_result.results
                    for doc in hc_result.documents or []:
                        print(f"\nDocument ID: {doc.id}")

                        # Entities
                        print("Entities:")
                        for entity in doc.entities or []:
                            print(f"  Text: {entity.text}")
                            print(f"  Category: {entity.category}")
                            print(f"  Offset: {entity.offset}")
                            print(f"  Length: {entity.length}")
                            print(f"  Confidence score: {entity.confidence_score}")
                            print()

                        # Relations
                        print("Relations:")
                        for relation in doc.relations or []:
                            print(f"  Relation type: {relation.relation_type}")
                            for rel_entity in relation.entities or []:
                                print(f"    Role: {rel_entity.role}")
                                print(f"    Ref: {rel_entity.ref}")
                            print()


# [END analyze_healthcare_entities_async]


async def main():
    await sample_analyze_healthcare_entities_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
