# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Create a hosted Reinforcement Learning Environment (RLE), then list the
    project's environments and the versions of the newly created environment.

USAGE:
    python sample_rle_environment_management.py \
        --name <new-rle-environment-name> \
        --acr-image-path <container-registry-image>

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" azure-identity python-dotenv

    Set FOUNDRY_PROJECT_ENDPOINT, or pass --endpoint. Authenticate locally
    with az login or another credential supported by DefaultAzureCredential.
"""

import argparse
import os

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Create and list hosted RLE environments.")
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("FOUNDRY_PROJECT_ENDPOINT"),
        help="Foundry project endpoint, or set FOUNDRY_PROJECT_ENDPOINT.",
    )
    parser.add_argument("--name", required=True, help="Name for the new hosted RLE environment.")
    parser.add_argument(
        "--acr-image-path",
        required=True,
        help="Container image reference in Azure Container Registry.",
    )
    args = parser.parse_args()

    if not args.endpoint:
        parser.error("provide --endpoint or set FOUNDRY_PROJECT_ENDPOINT")

    with DefaultAzureCredential() as credential:
        with AIProjectClient(endpoint=args.endpoint, credential=credential) as project_client:
            environment = project_client.rle.create_environment(
                name=args.name,
                acr_image_path=args.acr_image_path,
            )
            print(f"Created environment: {environment.name} (version {environment.version})")

            environments = project_client.rle.list_environments(limit=100)
            print("\nEnvironments:")
            for item in environments.data or []:
                print(f"- {item.name} (version {item.version})")

            versions = project_client.rle.list_environment_versions(environment.name, limit=100)
            print(f"\nVersions for {environment.name}:")
            for item in versions.data or []:
                print(f"- {item.version}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
