# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to enable distributed tracing with OpenTelemetry
    in Azure AI Inference client library and export traces to Azure Monitor.

    This sample assumes the AI model is hosted on a Serverless API or
    Managed Compute endpoint. For GitHub Models or Azure OpenAI endpoints,
    the client constructor needs to be modified. See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#key-concepts

USAGE:
    python sample_chat_completions_with_azure_monitor_tracing.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_CHAT_KEY - Your model key (a 32-character string). Keep it secret.
    3) APPLICATIONINSIGHTS_CONNECTION_STRING - Your Azure Monitor (Application Insights) connection string.
"""


import os
from opentelemetry import trace
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, CompletionsFinishReason
from azure.core.credentials import AzureKeyCredential
from azure.monitor.opentelemetry import configure_azure_monitor


 # [START trace_function]
from opentelemetry.trace import get_tracer
tracer = get_tracer(__name__)

# The tracer.start_as_current_span decorator will trace the function call and enable adding additional attributes
# to the span in the function implementation. Note that this will trace the function parameters and their values.
@tracer.start_as_current_span("get_temperature") # type: ignore
def get_temperature(city: str) -> str:

    # Adding attributes to the current span
    span = trace.get_current_span()
    span.set_attribute("requested_city", city)

    if city == "Seattle":
        return "75"
    elif city == "New York City":
        return "80"
    else:
        return "Unavailable"
 # [END trace_function]


def get_weather(city: str) -> str:
    if city == "Seattle":
        return "Nice weather"
    elif city == "New York City":
        return "Good weather"
    else:
        return "Unavailable"


def chat_completion_with_function_call(key, endpoint):
    import json
    from azure.ai.inference.models import ToolMessage, AssistantMessage, ChatCompletionsToolCall, ChatCompletionsToolDefinition, FunctionDefinition

    weather_description = ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            name="get_weather",
            description="Returns description of the weather in the specified city",
            parameters={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city for which weather info is requested",
                    },
                },
                "required": ["city"],
            },
        )
    )

    temperature_in_city = ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            name="get_temperature",
            description="Returns the current temperature for the specified city",
            parameters={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city for which temperature info is requested",
                    },
                },
                "required": ["city"],
            },
        )
    )

    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key), model="gpt-4o-mini")
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="What is the weather and temperature in Seattle?"),
    ]

    response = client.complete(messages=messages, tools=[weather_description, temperature_in_city])

    if response.choices[0].finish_reason == CompletionsFinishReason.TOOL_CALLS:
        # Append the previous model response to the chat history
        messages.append(AssistantMessage(tool_calls=response.choices[0].message.tool_calls))
        # The tool should be of type function call.
        if response.choices[0].message.tool_calls is not None and len(response.choices[0].message.tool_calls) > 0:
            for tool_call in response.choices[0].message.tool_calls:
                if type(tool_call) is ChatCompletionsToolCall:
                    function_args = json.loads(tool_call.function.arguments.replace("'", '"'))
                    print(f"Calling function `{tool_call.function.name}` with arguments {function_args}")
                    callable_func = globals()[tool_call.function.name]
                    function_response = callable_func(**function_args)
                    print(f"Function response = {function_response}")
                    # Provide the tool response to the model, by appending it to the chat history
                    messages.append(ToolMessage(tool_call_id=tool_call.id, content=function_response))
                    # With the additional tools information on hand, get another response from the model
            response = client.complete(messages=messages, tools=[weather_description, temperature_in_city])

    print(f"Model response = {response.choices[0].message.content}")


def main():
    # There is no need to pass APPLICATIONINSIGHTS_CONNECTION_STRING explicitly,
    # as it is read from this environment variable by the configure_azure_monitor function
    # It's provided here for clarity.
    configure_azure_monitor(connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"])

    try:
        endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
        key = os.environ["AZURE_AI_CHAT_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_CHAT_ENDPOINT' or 'AZURE_AI_CHAT_KEY'")
        print("Set them before running this sample.")
        exit()

    chat_completion_with_function_call(key, endpoint)

if __name__ == "__main__":
    main()
