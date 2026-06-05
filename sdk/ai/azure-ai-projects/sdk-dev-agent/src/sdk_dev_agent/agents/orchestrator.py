import json
import os

from dotenv import load_dotenv
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    BingGroundingSearchConfiguration,
    BingGroundingSearchToolParameters,
    BingGroundingTool,
    CodeInterpreterTool,
    PromptAgentDefinition,
)

from ..tools import functions as local_functions
from ..tools import tools as local_tools

load_dotenv()


def use_tools(response):
    """Run function_call items"""
    outputs: ResponseInputParam = []
    for item in response.output:
        if item.type == "function_call" and item.name in local_functions:
            args = json.loads(item.arguments) if item.arguments else {}
            result = local_functions[item.name](**args)
            outputs.append(
                FunctionCallOutput(
                    type="function_call_output",
                    call_id=item.call_id,
                    output=json.dumps(result),
                )
            )
    return outputs


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=credential,
    ) as project,
    project.get_openai_client() as openai_client,
):
    # Bing Grounding in Foundry
    bing = BingGroundingTool(
        bing_grounding=BingGroundingSearchToolParameters(
            search_configurations=[
                BingGroundingSearchConfiguration(
                    project_connection_id=os.environ["BING_PROJECT_CONNECTION_ID"],
                )
            ]
        )
    )

    agent = project.agents.create_version(
        agent_name="sdk-dev-agent",
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions=(
                "You are the SDK Dev Agent. You help users with the azure-ai-projects and azure-ai-agents Python SDKs.\n"
                "Tools:\n"
                "- read_repo: read a section of a file from the local"
                "azure-sdk-for-python repo. Use for READMEs, AGENTS.md, "
                "samples, source files. Always cite the repo-relative path.\n"
                "- BingGroundingTool: grounded web search via Bing. Use for "
                "looking up current docs, blog posts, or external references. "
                "Cite the source URLs.\n"
                "- CodeInterpreterTool: run Python in a sandbox to compute, "
                "validate snippets, or analyze data. Show the code and "
                "the result.\n"
                "\n"
                "Pick the right tool(s) per query."
            ),
            tools=[bing, CodeInterpreterTool(), *local_tools],
        ),
    )
    print(f"Agent: {agent.name} v{agent.version}")
    print("Type a message (or 'exit'/'quit' to leave).\n")

    try:
        previous_id = None
        while True:
            try:
                user_msg = input("you> ").strip()
            except EOFError:
                break
            if not user_msg:
                continue
            if user_msg.lower() in {"exit", "quit"}:
                break

            response = openai_client.responses.create(
                input=user_msg,
                extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                **({"previous_response_id": previous_id} if previous_id else {}),
            )
            for _ in range(5):
                outputs = use_tools(response)
                if not outputs:
                    break
                response = openai_client.responses.create(
                    input=outputs,
                    previous_response_id=response.id,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

            previous_id = response.id
            print(f"\nagent> {response.output_text}\n")
    finally:
        try:
            project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print(f"Deleted {agent.name} v{agent.version}")
        except Exception as exc:
            print(f"Cleanup failed for {agent.name}: {exc}")

