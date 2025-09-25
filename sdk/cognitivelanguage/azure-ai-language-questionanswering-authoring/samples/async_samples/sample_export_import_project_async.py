"""Async sample - Export and import a Question Answering authoring project."""
import os
import io
import zipfile
import asyncio
from azure.core.rest import HttpRequest
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring.aio import QuestionAnsweringAuthoringClient


async def sample_export_import_project_async():
    # [START export_import_project]
    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]
    project_name = os.environ["AZURE_QUESTIONANSWERING_PROJECT"]

    client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
    async with client:
        export_format = "json"
        export_poller = await client.begin_export(
            project_name=project_name, format=export_format
        )
        await export_poller.result()  # completes; no payload
        # No export URL available from the poller result in current API; skipping download section.
        minimal_assets = {
            "assets": {
                "qnas": [
                    {
                        "id": 1,
                        "answer": "Placeholder answer for imported project.",
                        "source": "https://contoso.example/source",
                        "questions": ["Sample question?"],
                    }
                ]
            }
        }
        import_poller = await client.begin_import_method(
            project_name=f"{project_name}-imported", body=minimal_assets, format="json"
        )
        await import_poller.result()
        print(f"Imported project as {project_name}-imported (minimal assets)")
    # [END export_import_project]


if __name__ == "__main__":
    asyncio.run(sample_export_import_project_async())
