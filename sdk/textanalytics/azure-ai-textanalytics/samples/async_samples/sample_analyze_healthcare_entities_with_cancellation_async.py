# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_healthcare_entities_with_cancellation.py

DESCRIPTION:
    This sample demonstrates how to cancel a Health job after it's been started.

USAGE:
    python sample_analyze_healthcare_entities_with_cancellation.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key
"""


import os
import asyncio
from azure.core.exceptions import HttpResponseError


async def sample_analyze_healthcare_entities_with_cancellation_async():
    # [START analyze_healthcare_entities_with_cancellation_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics.aio import TextAnalyticsClient

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )

    documents = [
        "RECORD #333582770390100 | MH | 85986313 | | 054351 | 2/14/2001 12:00:00 AM | \
        CORONARY ARTERY DISEASE | Signed | DIS | Admission Date: 5/22/2001 \
        Report Status: Signed Discharge Date: 4/24/2001 ADMISSION DIAGNOSIS: \
        CORONARY ARTERY DISEASE. HISTORY OF PRESENT ILLNESS: \
        The patient is a 54-year-old gentleman with a history of progressive angina over the past several months. \
        The patient had a cardiac catheterization in July of this year revealing total occlusion of the RCA and \
        50% left main disease , with a strong family history of coronary artery disease with a brother dying at \
        the age of 52 from a myocardial infarction and another brother who is status post coronary artery bypass grafting. \
        The patient had a stress echocardiogram done on July , 2001 , which showed no wall motion abnormalities ,\
        but this was a difficult study due to body habitus. The patient went for six minutes with minimal ST depressions \
        in the anterior lateral leads , thought due to fatigue and wrist pain , his anginal equivalent. Due to the patient's \
        increased symptoms and family history and history left main disease with total occasional of his RCA was referred \
        for revascularization with open heart surgery."
    ]

    async with text_analytics_client:
        poller = await text_analytics_client.begin_analyze_healthcare_entities(documents)

        try:
            cancellation_poller = await poller.cancel()
            await cancellation_poller.wait()

        except HttpResponseError as e:
            # If the operation has already reached a terminal state it cannot be cancelled.
            print(e)

        else:
            print("Healthcare entities analysis was successfully cancelled.")

    # [END analyze_healthcare_entities_with_cancellation_async]


async def main():
    await sample_analyze_healthcare_entities_with_cancellation_async()


if __name__ == '__main__':
    asyncio.run(main())


