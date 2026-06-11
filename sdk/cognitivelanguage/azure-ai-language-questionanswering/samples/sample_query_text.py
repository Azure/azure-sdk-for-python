# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_query_text.py

DESCRIPTION:
    Ask a question over ad-hoc text (options object pattern).

USAGE:
    python sample_query_text.py

Environment variables:
    1) AZURE_QUESTIONANSWERING_ENDPOINT
    2) AZURE_QUESTIONANSWERING_KEY
"""

from __future__ import annotations


def sample_query_text():
    # [START query_text]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.questionanswering import QuestionAnsweringClient
    from azure.ai.language.questionanswering.models import AnswersFromTextOptions, TextDocument

    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]

    client = QuestionAnsweringClient(endpoint, AzureKeyCredential(key))
    with client:
        question = "How long does it take to charge a Surface?"

        # Options object call
        options = AnswersFromTextOptions(
            question=question,
            text_documents=[
                TextDocument(
                    id="doc1",
                    text=(
                        "Power and charging. It takes two to four hours to charge the Surface Pro 4 battery fully "
                        "from an empty state. It can take longer if you're using your Surface for power-intensive "
                        "activities like gaming or video streaming while you're charging it."
                    ),
                ),
                TextDocument(
                    id="doc2",
                    text=(
                        "You can use the USB port on your Surface Pro 4 power supply to charge other devices, like "
                        "a phone, while your Surface charges. The USB port on the power supply is only for charging, "
                        "not for data transfer."
                    ),
                ),
            ],
        )

        output = client.get_answers_from_text(options)
        best_answer = next(
            (a for a in (output.answers or []) if a.confidence and a.confidence > 0.9),
            None,
        )
        if best_answer:
            print(f"Q: {question}")
            print(f"A: {best_answer.answer}")
        else:
            print(f"No answers for '{question}'")

    # [END query_text]


if __name__ == "__main__":
    sample_query_text()
