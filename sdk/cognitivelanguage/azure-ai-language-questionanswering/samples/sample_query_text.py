# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_query_text.py

DESCRIPTION:
    This sample demonstrates how to ask a question from supplied text data.

USAGE:
    python sample_query_text.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_QUESTIONANSWERING_ENDPOINT - the endpoint to your QuestionAnswering resource.
    2) AZURE_QUESTIONANSWERING_KEY - your QuestionAnswering API key.
"""


def sample_query_text():
    # [START query_text]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.questionanswering import QuestionAnsweringClient
    from azure.ai.language.questionanswering import models as qna

    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]

    client = QuestionAnsweringClient(endpoint, AzureKeyCredential(key))
    with client:
        input = qna.TextQueryOptions(
            question="How long it takes to charge surface?",
            records=[
                qna.TextRecord(
                    text="Power and charging. It takes two to four hours to charge the Surface Pro 4 battery fully from an empty state. " +
                         "It can take longer if you’re using your Surface for power-intensive activities like gaming or video streaming while you’re charging it.",
                    id="doc1"
                ),
                qna.TextRecord(
                    text="You can use the USB port on your Surface Pro 4 power supply to charge other devices, like a phone, while your Surface charges. " +
                         "The USB port on the power supply is only for charging, not for data transfer. If you want to use a USB device, plug it into the USB port on your Surface.",
                    id="doc2"
                )
            ]
        )

        output = client.query_text(input)

        best_answer = [a for a in output.answers if a.confidence_score > 0.9][0]
        print("Q: {}".format(input.question))
        print("A: {}".format(best_answer.answer))

    # [END query_text]


if __name__ == '__main__':
    sample_query_text()
