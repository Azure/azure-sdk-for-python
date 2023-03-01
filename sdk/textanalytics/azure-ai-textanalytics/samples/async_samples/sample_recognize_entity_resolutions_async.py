# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_entity_resolutions_async.py

DESCRIPTION:
    This sample shows to recognize entity resolutions in text documents. You must pass
    model_version="2022-10-01-preview" to receive resolutions in the response.

    See https://aka.ms/azsdk/language/ner-resolutions for a list of all possible resolutions.

USAGE:
    python sample_recognize_entity_resolutions_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key
"""

import asyncio


async def sample_recognize_entity_resolutions_async() -> None:
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics.aio import TextAnalyticsClient
    from azure.ai.textanalytics import ResolutionKind

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]
    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    async with text_analytics_client:
        documents = [
            "The cat is 3 years old and weighs ten pounds.",

            "The bill for $25.45 is for service between January 1, 2023 and February 2, 2023. "
            "A discount is applied since the internet dropped below 50 mB/s.",

            "He was the first man to walk on the moon on July 21, 1969 at 2:56pm.",

            "The property spans 25 acres and has a 3 mile round-trip hiking trail.",

            "This aircraft carries 200 liters of fuel and can fly 65-80 passengers. "
            "Cruising speed is 150 knots at standard 32°F temperature and pressure",
        ]

        results = await text_analytics_client.recognize_entities(documents, model_version="2022-10-01-preview")

    for document, result in zip(documents, results):
        print(f"\nResults for document: '{document}'")
        if result.is_error is True:
            print(f"Document Error - {result.error.code}: {result.error.message}")
            continue

        for entity in result.entities:
            print(f"...Entity is '{entity.text}' and categorized as '{entity.category}' "
                  f"with subcategory '{entity.subcategory}'.")
            for res in entity.resolutions:
                if res.resolution_kind == ResolutionKind.AGE_RESOLUTION:
                    print(f"......Age resolution has a value of '{res.value}' and unit of '{res.unit}'.")
                elif res.resolution_kind == ResolutionKind.AREA_RESOLUTION:
                    print(f"......Area resolution has a value of '{res.value}' and unit of '{res.unit}'.")
                elif res.resolution_kind == ResolutionKind.CURRENCY_RESOLUTION:
                    print(f"......Currency resolution has a value of '{res.value}', unit of '{res.unit}', "
                          f"and ISO4217 code of '{res.iso4217}'.")
                elif res.resolution_kind == ResolutionKind.DATE_TIME_RESOLUTION:
                    print(f"......DateTime resolution has a value of '{res.value}', a subkind of "
                          f"'{res.date_time_sub_kind}', and a timex of '{res.timex}'.")
                elif res.resolution_kind == ResolutionKind.INFORMATION_RESOLUTION:
                    print(f"......Information resolution has a value of '{res.value}' and unit of '{res.unit}'.")
                elif res.resolution_kind == ResolutionKind.LENGTH_RESOLUTION:
                    print(f"......Length resolution has a value of '{res.value}' and unit of '{res.unit}'.")
                elif res.resolution_kind == ResolutionKind.NUMBER_RESOLUTION:
                    print(f"......Number resolution has a kind of '{res.number_kind}' and a value of '{res.value}.")
                elif res.resolution_kind == ResolutionKind.NUMERIC_RANGE_RESOLUTION:
                    print(f"......Numeric range resolution has a kind of '{res.range_kind}', a minimum of "
                          f"'{res.minimum}' and a maximum of '{res.maximum}'.")
                elif res.resolution_kind == ResolutionKind.ORDINAL_RESOLUTION:
                    print(f"......Ordinal resolution has a value of '{res.value}', an offset of '{res.offset}', "
                          f"and is relative to '{res.relative_to}'.")
                elif res.resolution_kind == ResolutionKind.SPEED_RESOLUTION:
                    print(f"......Speed resolution has a value of '{res.value}' and unit of '{res.unit}'.")
                elif res.resolution_kind == ResolutionKind.TEMPERATURE_RESOLUTION:
                    print(f"......Temperature resolution has a value of '{res.value}' and unit of '{res.unit}'.")
                elif res.resolution_kind == ResolutionKind.TEMPORAL_SPAN_RESOLUTION:
                    print(f"......Temporal span resolution begins on '{res.begin}' and ends on '{res.end}' "
                          f"with duration '{res.duration}'.")
                elif res.resolution_kind == ResolutionKind.VOLUME_RESOLUTION:
                    print(f"......Volume resolution has a value of '{res.value}' and unit of '{res.unit}'.")
                elif res.resolution_kind == ResolutionKind.WEIGHT_RESOLUTION:
                    print(f"......Weight resolution has a value of '{res.value}' and unit of '{res.unit}'.")


async def main():
    await sample_recognize_entity_resolutions_async()


if __name__ == '__main__':
    asyncio.run(main())
