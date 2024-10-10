# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to use Azure AI client to get Inference client and
    instrument it with traces using Inference Instumentor that is also acquired
    using the Azure AI Client.
"""
import os
from opentelemetry import trace
from azure.ai.client import AzureAIClient
from azure.identity import DefaultAzureCredential
from azure.ai.inference.models import SystemMessage, UserMessage, CompletionsFinishReason
# opentelemetry-sdk is required for the opentelemetry.sdk imports.
# You can install it with command "pip install opentelemetry-sdk".
#from opentelemetry.sdk.trace import TracerProvider
#from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

 # [START trace_setting]
from azure.core.settings import settings
settings.tracing_implementation = "opentelemetry"
# [END trace_setting]

# Setup tracing to console
# Requires opentelemetry-sdk
#exporter = ConsoleSpanExporter()
#trace.set_tracer_provider(TracerProvider())
#tracer = trace.get_tracer(__name__)
#trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))

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


def chat_completion_with_function_call(client):
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
    # Create an Azure AI Client from a connection string, copied from your AI Studio project.
    # It should have the format "<Endpoint>;<AzureSubscriptionId>;<ResourceGroup>;<WorkspaceName>"
    ai_client = AzureAIClient.from_connection_string(
        credential=DefaultAzureCredential(),
        connection=os.environ["AI_CLIENT_CONNECTION_STRING"],
    )

    # Or, you can create the Azure AI Client by giving all required parameters directly
    # ai_client = AzureAIClient(
    #     credential=DefaultAzureCredential(),
    #     endpoint=os.environ["AI_CLIENT_ENDPOINT"],
    #     subscription_id=os.environ["AI_CLIENT_SUBSCRIPTION_ID"],
    #     resource_group_name=os.environ["AI_CLIENT_RESOURCE_GROUP_NAME"],
    #     workspace_name=os.environ["AI_CLIENT_WORKSPACE_NAME"],
    # )

    # Get an authenticated OpenAI client for your default Azure OpenAI connection:
    client = ai_client.inference.get_azure_openai_client()

    # [START instrument_inferencing]
    # Speficy a semantic conventions version used for the instrumentation if needed.
    #instrumentor = ai_client.tracing.create_inference_instrumentor(SemanticConventionsVersion.PREVIEW)
    
    # If you do not specify semantic conventions version, then the default version supported by the current
    # Inference SDK will be returned.
    instrumentor = ai_client.tracing.create_inference_instrumentor()
    
    # Instrument AI Inference API
    instrumentor.instrument()
    # [END instrument_inferencing]

    chat_completion_with_function_call(client)

    # [START uninstrument_inferencing]
    instrumentor.uninstrument()
    # [END uninstrument_inferencing]


if __name__ == "__main__":
    main()
