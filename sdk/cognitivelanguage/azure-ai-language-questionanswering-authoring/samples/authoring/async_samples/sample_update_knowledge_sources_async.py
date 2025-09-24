"""Async sample - Update project knowledge sources and add QnAs & synonyms."""
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring.aio import QuestionAnsweringAuthoringClient


async def sample_update_knowledge_sources_async():
    # [START update_knowledge_sources]
    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]

    client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
    async with client:
        project_name = "MicrosoftFAQProject"
        await client.create_project(
            project_name=project_name,
            options={
                "description": "Test project for some Microsoft QnAs",
                "language": "en",
                "multilingualResource": True,
                "settings": {"defaultAnswer": "no answer"},
            },
        )

        sources_poller = await client.begin_update_sources(
            project_name=project_name,
            sources=[
                {
                    "op": "add",
                    "value": {
                        "displayName": "MicrosoftFAQ",
                        "source": "https://www.microsoft.com/en-in/software-download/faq",
                        "sourceUri": "https://www.microsoft.com/en-in/software-download/faq",
                        "sourceKind": "url",
                        "contentStructureKind": "unstructured",
                        "refresh": False,
                    },
                }
            ],
        )
        sources = await sources_poller.result()
        async for item in sources:
            print(f"Source: {item.get('displayName', 'N/A')} -> {item.get('sourceUri', 'N/A')}")

        qna_poller = await client.begin_update_qnas(
            project_name=project_name,
            qnas=[
                {
                    "op": "add",
                    "value": {
                        "questions": [
                            "What is the easiest way to use azure services in my .NET project?",
                        ],
                        "answer": "Using Microsoft's Azure SDKs",
                    },
                }
            ],
        )
        qnas = await qna_poller.result()
        async for item in qnas:
            print(f"QnA {item['id']} -> answer: {item['answer']}")

        await client.update_synonyms(
            project_name=project_name,
            synonyms={
                "value": [
                    {"alterations": ["qnamaker", "qna maker"]},
                    {"alterations": ["qna", "question and answer"]},
                ]
            },
        )
        synonyms = client.list_synonyms(project_name=project_name)
        async for item in synonyms:
            print("Synonyms group:")
            for alt in item["alterations"]:
                print(f"  {alt}")
    # [END update_knowledge_sources]


if __name__ == "__main__":
    asyncio.run(sample_update_knowledge_sources_async())
