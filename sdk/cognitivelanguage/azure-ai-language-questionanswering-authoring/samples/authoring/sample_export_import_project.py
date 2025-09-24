"""Sample - Export and import a Question Answering authoring project.

Shows how to:
  * Export an existing project to JSON
  * Re-import the assets as a new project

Environment variables required:
  * AZURE_QUESTIONANSWERING_ENDPOINT
  * AZURE_QUESTIONANSWERING_KEY
  * AZURE_QUESTIONANSWERING_PROJECT - existing project to export

Run with: python sample_export_import_project.py
"""

import os
import io
import zipfile
from azure.core.rest import HttpRequest
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient


def sample_export_import_project():
    # [START export_import_project]
    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]
    project_name = os.environ["AZURE_QUESTIONANSWERING_PROJECT"]

    client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
    with client:
        export_format = "json"
        export_poller = client.begin_export(project_name=project_name, file_format=export_format)
        export_result = export_poller.result()
        export_url = export_result["resultUrl"]
        request = HttpRequest("GET", export_url)

        if export_format == "json":
            response = client.send_request(request)
            exported_project = response.json()
        else:  # excel or tsv
            response = client.send_request(request, stream=True)
            exported_zip = zipfile.ZipFile(io.BytesIO(response.read()))
            exported_zip.extractall("./ExportedProject")
            exported_zip.close()
            print(f"{export_format} project files written to ./ExportedProject.")
            return

        import_poller = client.begin_import_assets(
            project_name=f"{project_name}-imported", options=exported_project
        )
        import_poller.result()
        print(f"Imported project as {project_name}-imported")
    # [END export_import_project]


if __name__ == "__main__":
    sample_export_import_project()
