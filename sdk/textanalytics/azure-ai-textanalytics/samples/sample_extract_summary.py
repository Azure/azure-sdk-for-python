# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_extract_summary.py

DESCRIPTION:
    This sample demonstrates how to submit text documents for extractive text summarization.
    Extractive summarization is available as an action type through the begin_analyze_actions API.

USAGE:
    python sample_extract_summary.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""


import os


def sample_extractive_summarization():
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import (
        TextAnalyticsClient,
        ExtractSummaryAction
    )

    endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
    key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )

    document = [
        "The government of British Prime Minster Theresa May has been plunged into turmoil with the resignation"
        " of two senior Cabinet ministers in a deep split over her Brexit strategy. The Foreign Secretary Boris "
        "Johnson, quit on Monday, hours after the resignation late on Sunday night of the minister in charge of "
        "Brexit negotiations, David Davis. Their decision to leave the government came three days after May "
        "appeared to have agreed a deal with herfractured Cabinet on the UK's post Brexit relationship with "
        "the EU. That plan is now in tatters and her political future appears uncertain. May appeared in Parliament"
        " on Monday afternoon to defend her plan, minutes after Downing Street confirmed the departure of Johnson. "
        "May acknowledged the splits in her statement to MPs, saying of the ministers who quit: We do not agree "
        "about the best way of delivering our shared commitment to honoring the result of the referendum. The "
        "Prime Minister's latest plitical drama began late on Sunday night when Davis quit, declaring he could "
        "not support May's Brexit plan. He said it involved too close a relationship with the EU and gave only "
        "an illusion of control being returned to the UK after it left the EU. It seems to me we're giving too "
        "much away, too easily, and that's a dangerous strategy at this time, Davis said in a BBC radio "
        "interview Monday morning. Johnson's resignation came Monday afternoon local time, just before the "
        "Prime Minister was due to make a scheduled statement in Parliament. This afternoon, the Prime Minister "
        "accepted the resignation of Boris Johnson as Foreign Secretary, a statement from Downing Street said."
    ]

    poller = text_analytics_client.begin_analyze_actions(
        document,
        actions=[
            ExtractSummaryAction(),
        ],
    )

    document_results = poller.result()
    for result in document_results:
        extract_summary_result = result[0]  # first document, first result
        if extract_summary_result.is_error:
            print("...Is an error with code '{}' and message '{}'".format(
                extract_summary_result.code, extract_summary_result.message
            ))
        else:
            print("Summary extracted: \n{}".format(
                " ".join([sentence.text for sentence in extract_summary_result.sentences]))
            )


if __name__ == "__main__":
    sample_extractive_summarization()
