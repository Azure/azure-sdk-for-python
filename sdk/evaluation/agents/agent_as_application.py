"""
DESCRIPTION:
    This demonstrates how to evaluate agents as application.
USAGE:
    pip install azure-ai-projects azure-identity
    pip install git+https://github.com/Azure/azure-sdk-for-python.git@users/singanking/agents_evaluation_mock#egg=azure-ai-evaluation&subdirectory=sdk/evaluation/azure-ai-evaluation

    Set these environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import json
import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType, RunStepType, ToolSet, FunctionTool, RunStepFunctionToolCallDetails, \
    RunStepFunctionToolCall, ThreadMessage, MessageTextContent, MessageTextDetails
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from azure.ai.evaluation import RelevanceEvaluator, CoherenceEvaluator, evaluate, FunctionToolAccuracyEvaluator
from user_functions import user_functions
load_dotenv()

functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)

get_location_api_spec = """
openapi: 3.0.0
info:
  title: GetLocationAPI
  version: 1.0.0
paths:
  /getLocation:
    get:
      summary: Get the location of a place
      parameters:
        - in: query
          name: location
          schema:
            type: string
          required: true
          description: The name of the location to get the address for
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  address:
                    type: string
"""

opening_hours_api_spec = """
openapi: 3.0.0
info:
  title: OpeningHoursAPI
  version: 1.0.0
paths:
  /getOpeningHours:
    get:
      summary: Get the opening hours of a place
      parameters:
        - in: query
          name: location
          schema:
            type: string
          required: true
          description: The name of the location to get the opening hours for
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  opening_hours:
                    type: string
"""

ticket_price_api_spec = """
openapi: 3.0.0
info:
  title: TicketPriceAPI
  version: 1.0.0
paths:
  /getTicketPrice:
    get:
      summary: Get the ticket prices for a place
      parameters:
        - in: query
          name: location
          schema:
            type: string
          required: true
          description: The name of the location to get the ticket prices for
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  adult_price:
                    type: number
                  child_price:
                    type: number
"""

tools_definitions = [get_location_api_spec, opening_hours_api_spec, ticket_price_api_spec]

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

model_config = project_client.connections.get_default(
                connection_type=ConnectionType.AZURE_OPEN_AI,
                include_credentials=True).to_evaluator_model_config(
                                            deployment_name=os.environ["MODEL_DEPLOYMENT_NAME"],
                                            api_version=os.environ["API_VERSION"],
                                            include_credentials=True
                                          )
agent = project_client.agents.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="Seattle Tourist Assistant",
    instructions="You are helpful assistant that helps answer queries about Seattle and place to visit in and around Seattle",
    toolset=toolset,
)

class ThreadMessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (RunStepFunctionToolCallDetails, RunStepFunctionToolCall, MessageTextDetails, MessageTextContent)):
            return obj.__dict__["_data"]
        if isinstance(obj, ThreadMessage):
            json_data = obj.__dict__["_data"]
            if obj.__dict__.get("tool_calls"):
                json_data["tool_calls"] = obj.__dict__["tool_calls"]
            return json_data  # or implement a method to convert to a dictionary
        return super().default(obj)

def seattle_tourist_assistant(query: str):
    thread = project_client.agents.create_thread()
    message = project_client.agents.create_message(
        thread_id=thread.id, role="user", content=query
    )

    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    # [END create_and_process_run]
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    messages = project_client.agents.list_messages(thread_id=thread.id)
    run_step_details = project_client.agents.list_run_steps(thread_id=thread.id, run_id=run.id)
    tool_calls = []
    for run_step in run_step_details.data:
        if run_step.type == RunStepType.TOOL_CALLS:
            tool_calls.extend(run_step.step_details.tool_calls)

    tool_calls = json.dumps(tool_calls, cls=ThreadMessageEncoder)

    return {"response": messages.data[0].content[0].text.value, "tool_calls": json.loads(tool_calls)}

relevance_evaluator = RelevanceEvaluator(model_config)
function_tool_accuracy_evaluator = FunctionToolAccuracyEvaluator(
    model_config,
    tools_definitions
)


if __name__ == "__main__":
    results = evaluate(
        data="data.jsonl",
        target=seattle_tourist_assistant,
        evaluators={
            "relevance": relevance_evaluator,
            "function_tool_accuracy": function_tool_accuracy_evaluator,
        },
    )

    print(json.dumps(dict(results)))