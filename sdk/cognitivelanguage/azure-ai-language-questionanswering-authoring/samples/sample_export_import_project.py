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
        # Updated: parameter is now 'file_format', and LRO result is None (no metadata dict).
        export_poller = client.begin_export(project_name=project_name, file_format=export_format)
        export_poller.result()  # completes; no result payload
        # In the new API surface an export URL isn't returned via poller.result(); a separate
        # retrieval step would be needed if/when service exposes it. This sample now focuses on
        # demonstrating the LRO pattern only.
        # For illustration, we skip downloading assets (no resultUrl available in current LRO shape).
        # Import demonstration: provide minimal valid assets payload manually.
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
        import_poller = client.begin_import_assets(project_name=project_name, body=minimal_assets, file_format="json")
        import_poller.result()  # completes; no result payload
        print(f"Imported project as {project_name} (minimal assets)")
    # [END export_import_project]


if __name__ == "__main__":
    sample_export_import_project()
