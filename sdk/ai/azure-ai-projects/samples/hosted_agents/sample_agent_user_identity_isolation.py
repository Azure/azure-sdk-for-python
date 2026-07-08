# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates per-user Hosted Agent isolation while sending
    delegated end-user identities in the `x-ms-user-identity` header.

    It packages the basic hosted-agent source folder as a new Hosted Agent
    version, routes the `MyHostedAgent` endpoint to that version, and then
    invokes the same Hosted Agent as two different delegated users. The sample
    shows that a follow-up request can continue a prior response chain only
    when the delegated user identity matches the user who started it:

    * First delegated user: "1 + 1 = ?" then "then + 10" -> 12
    * Second delegated user: attempting "then + 10" against the first user's
      response chain is expected to fail with `404 NotFound`, confirming the
      response history is isolated per delegated user.

USAGE:
    python sample_agent_user_identity_isolation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model.
    3) FOUNDRY_HOSTED_AGENT_NAME - Optional. The Hosted Agent name. Defaults to
       `MyHostedAgent`.
    4) DELEGATED_USER_IDENTITY - Optional fixed delegated user identity to use
        for the first request chain. If omitted, a random UUID is generated.
    5) DELEGATED_USER_IDENTITY_2 - Optional fixed delegated user identity to
        use for the second user. If omitted, a random UUID is generated.
"""

import os
import sys
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from openai import NotFoundError

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeConfiguration,
    CodeDependencyResolution,
    HostedAgentDefinition,
    ProtocolVersionRecord,
)

_SAMPLES_DIR = Path(__file__).resolve().parents[1]
if str(_SAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(_SAMPLES_DIR))

from hosted_agents_util import create_version_from_code
from util import zip_directory

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
agent_name = os.environ.get("FOUNDRY_HOSTED_AGENT_NAME", "MyHostedAgent")
delegated_user_identity = os.environ.get("DELEGATED_USER_IDENTITY", str(uuid4()))
delegated_user_identity_2 = os.environ.get("DELEGATED_USER_IDENTITY_2", str(uuid4()))
hosted_agent_source_dir = Path(__file__).parent / "assets" / "basic-agent"

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    zip_filename = "basic-agent.zip"
    zip_path = zip_directory(hosted_agent_source_dir, zip_filename)[2]

    with (
        zip_path.open("rb") as code_stream,
        create_version_from_code(
            project_client,
            agent_name=agent_name,
            code=code_stream,
            description="Hosted agent version for delegated user identity isolation.",
            definition=HostedAgentDefinition(
                cpu="0.5",
                memory="1Gi",
                code_configuration=CodeConfiguration(
                    runtime="python_3_14",
                    entry_point=["python", "main.py"],
                    dependency_resolution=CodeDependencyResolution.REMOTE_BUILD,
                ),
                environment_variables={
                    "FOUNDRY_PROJECT_ENDPOINT": endpoint,
                    "FOUNDRY_MODEL_NAME": model_name,
                    "AGENT_INSTRUCTIONS": (
                        "You are a helpful assistant that answers arithmetic questions. "
                        "Use the prior response context to resolve follow-up math questions like 'then + 10'."
                    ),
                },
                protocol_versions=[ProtocolVersionRecord(protocol="responses", version="2.0.0")],
            ),
        ) as created_version,
        project_client.get_openai_client(agent_name=agent_name) as openai_client,
    ):
        print("User 1 input: 1 + 1 = ?")
        response = openai_client.responses.create(
            input="1 + 1 = ?",
            extra_headers={"x-ms-user-identity": delegated_user_identity},
        )
        print(f"Agent: {response.output_text}")

        print(
            "User 2 input: Add 10 to previous result.  Check out if the agent can continue the previous response chain from User 1."
        )
        try:
            openai_client.responses.create(
                input="Add 10 to previous result",
                previous_response_id=response.id,
                extra_headers={"x-ms-user-identity": delegated_user_identity_2},
            )
            print(f"Agent: {response.output_text}")
        except NotFoundError as e:
            print(
                "Agent: Expected isolation behavior confirmed. "
                "A different delegated user cannot continue the previous response chain and must start a new conversation."
            )

        print(
            "User 1 input: Add 10 to previous result, Check out if the agent can continue the previous response chain from User 1."
        )
        response = openai_client.responses.create(
            input="Add 10 to previous result",
            previous_response_id=response.id,
            extra_headers={"x-ms-user-identity": delegated_user_identity},
        )
        print(f"Agent: {response.output_text}")
