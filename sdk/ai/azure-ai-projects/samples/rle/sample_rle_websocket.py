# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Connect to a leased OpenEnv instance over WebSocket, send one text message, and print the
    response. The Slice 2 service contract supports complete text messages only.

USAGE:
    python sample_rle_websocket.py --name <rle-environment-name> --message <text>

    Set FOUNDRY_PROJECT_ENDPOINT and optionally RLE_ENV_NAME and RLE_ENV_VERSION.
    Authenticate locally with `az login` or another credential supported by DefaultAzureCredential.
"""

import argparse
import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Send a text message to an OpenEnv WebSocket."
    )
    parser.add_argument(
        "--endpoint", default=os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
    )
    parser.add_argument("--name", default=os.environ.get("RLE_ENV_NAME"))
    parser.add_argument("--version", default=os.environ.get("RLE_ENV_VERSION"))
    parser.add_argument("--message", required=True)
    args = parser.parse_args()

    if not args.endpoint:
        parser.error("provide --endpoint or set FOUNDRY_PROJECT_ENDPOINT")
    if not args.name:
        parser.error("provide --name or set RLE_ENV_NAME")

    with DefaultAzureCredential() as credential:
        with AIProjectClient(
            endpoint=args.endpoint, credential=credential, allow_preview=True
        ) as project_client:
            with project_client.rle.get_openenv_client(
                name=args.name, version=args.version
            ) as openenv_client:
                with openenv_client.get_instance() as instance:
                    with instance.open_websocket() as websocket:
                        websocket.send(args.message)
                        print(websocket.recv())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
