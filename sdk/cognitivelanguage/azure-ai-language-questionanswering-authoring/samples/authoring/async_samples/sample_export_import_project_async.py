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
            project_name=project_name, file_format=export_format
        )
        export_result = await export_poller.result()
        export_url = export_result["resultUrl"]
        request = HttpRequest("GET", export_url)

        if export_format == "json":
            response = await client.send_request(request)
            exported_project = response.json()
        else:  # excel or tsv
            response = await client.send_request(request, stream=True)
            exported_zip = zipfile.ZipFile(io.BytesIO(await response.read()))
            exported_zip.extractall("./ExportedProject")
            exported_zip.close()
            print(f"{export_format} project files written to ./ExportedProject.")
            return

        import_poller = await client.begin_import_assets(
            project_name=f"{project_name}-imported", options=exported_project
        )
        await import_poller.result()
        print(f"Imported project as {project_name}-imported")
    # [END export_import_project]


if __name__ == "__main__":
    asyncio.run(sample_export_import_project_async())
