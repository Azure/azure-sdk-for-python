"""Sample - Update project knowledge sources and add QnAs & synonyms.

Demonstrates:
  * Creating a project
  * Adding a URL knowledge source
  * Adding QnA pairs
  * Adding synonyms

Environment variables required:
  * AZURE_QUESTIONANSWERING_ENDPOINT
  * AZURE_QUESTIONANSWERING_KEY

Run with: python sample_update_knowledge_sources.py
"""

import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient, models as _models


def sample_update_knowledge_sources():
    # [START update_knowledge_sources]
    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]

    client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
    with client:
        project_name = "MicrosoftFAQProject"
        client.create_project(
            project_name=project_name,
            options={
                "description": "Test project for some Microsoft QnAs",
                "language": "en",
                "multilingualResource": True,
                "settings": {"defaultAnswer": "no answer"},
            },
        )

        sources_poller = client.begin_update_sources(
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
        sources_poller.result()
        print("Knowledge source added (MicrosoftFAQ)")

        qna_poller = client.begin_update_qnas(
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
        qna_poller.result()
        print("QnA added (1 record)")

        client.update_synonyms(
            project_name=project_name,
            synonyms=_models.SynonymAssets(
                value=[
                    _models.WordAlterations(alterations=["qnamaker", "qna maker"]),
                    _models.WordAlterations(alterations=["qna", "question and answer"]),
                ]
            ),
        )
        synonyms = client.list_synonyms(project_name=project_name)
        for item in synonyms:  # ItemPaged
            print("Synonyms group:")
            for alt in item["alterations"]:
                print(f"  {alt}")
    # [END update_knowledge_sources]


if __name__ == "__main__":
    sample_update_knowledge_sources()
