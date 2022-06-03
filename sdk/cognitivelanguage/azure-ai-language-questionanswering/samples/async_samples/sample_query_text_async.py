# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_query_text_async.py

DESCRIPTION:
    This sample demonstrates how to ask a question from supplied text data.

USAGE:
    python sample_query_text_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_QUESTIONANSWERING_ENDPOINT - the endpoint to your QuestionAnswering resource.
    2) AZURE_QUESTIONANSWERING_KEY - your QuestionAnswering API key.
"""
import asyncio


async def sample_query_text():
    # [START query_text_async]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.questionanswering.aio import QuestionAnsweringClient
    from azure.ai.language.questionanswering import models as qna

    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]

    client = QuestionAnsweringClient(endpoint, AzureKeyCredential(key))
    async with client:
        input = qna.AnswersFromTextOptions(
            question="How long it takes to charge surface?",
            text_documents=[
                "Power and charging. It takes two to four hours to charge the Surface Pro 4 battery fully from an empty state. " +
                "It can take longer if you’re using your Surface for power-intensive activities like gaming or video streaming while you’re charging it.",
                "You can use the USB port on your Surface Pro 4 power supply to charge other devices, like a phone, while your Surface charges. " +
                "The USB port on the power supply is only for charging, not for data transfer. If you want to use a USB device, plug it into the USB port on your Surface.",
            ]
        )

        output = await client.get_answers_from_text(input)

        best_answer = [a for a in output.answers if a.confidence > 0.9][0]
        print("Q: {}".format(input.question))
        print("A: {}".format(best_answer.answer))

    # [END query_text_async]


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sample_query_text())
