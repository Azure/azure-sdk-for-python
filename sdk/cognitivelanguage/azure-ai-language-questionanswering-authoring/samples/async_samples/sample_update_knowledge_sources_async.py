# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Async sample - Update project knowledge sources and add QnAs & synonyms."""

import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring.aio import QuestionAnsweringAuthoringClient
from azure.ai.language.questionanswering.authoring import models as _models


async def sample_update_knowledge_sources_async():
    # [START update_knowledge_sources]
    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]

    client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
    async with client:
        project_name = "MicrosoftFAQProject"
        await client.create_project( # pylint: disable=no-value-for-parameter
            project_name=project_name,
            options={
                "description": "Test project for some Microsoft QnAs",
                "language": "en",
                "multilingualResource": True,
                "settings": {"defaultAnswer": "no answer"},
            },
        )

        sources_poller = await client.begin_update_sources( # pylint: disable=no-value-for-parameter
            project_name=project_name,
            sources=[
                _models.UpdateSourceRecord(
                    op="add",
                    value=_models.UpdateQnaSourceRecord(
                        display_name="MicrosoftFAQ",
                        source="https://www.microsoft.com/en-in/software-download/faq",
                        source_uri="https://www.microsoft.com/en-in/software-download/faq",
                        source_kind="url",
                        content_structure_kind="unstructured",
                        refresh=False,
                    ),
                )
            ],
        )
        await sources_poller.result()
        print("Knowledge source added (MicrosoftFAQ)")

        qna_poller = await client.begin_update_qnas( # pylint: disable=no-value-for-parameter
            project_name=project_name,
            qnas=[
                _models.UpdateQnaRecord(
                    op="add",
                    value=_models.QnaRecord(
                        id=1,
                        questions=["What is the easiest way to use azure services in my .NET project?"],
                        answer="Using Microsoft's Azure SDKs",
                        source="manual",
                    ),
                )
            ],
        )
        await qna_poller.result()
        print("QnA added (1 record)")

        await client.update_synonyms( # pylint: disable=no-value-for-parameter
            project_name=project_name,
            synonyms=_models.SynonymAssets(
                value=[
                    _models.WordAlterations(alterations=["qnamaker", "qna maker"]),
                    _models.WordAlterations(alterations=["qna", "question and answer"]),
                ]
            ),
        )
        synonyms = client.list_synonyms(project_name=project_name)
        async for item in synonyms:
            print("Synonyms group:")
            for alt in item["alterations"]:
                print(f"  {alt}")
    # [END update_knowledge_sources]


if __name__ == "__main__":
    asyncio.run(sample_update_knowledge_sources_async())
