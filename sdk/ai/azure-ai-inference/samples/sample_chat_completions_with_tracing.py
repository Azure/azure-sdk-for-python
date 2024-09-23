# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, CompletionsFinishReason
from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.ai.inference import AIInferenceApiInstrumentor
from azure.core.settings import settings


# Setup tracing to console
exporter = ConsoleSpanExporter()
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))

# Use the following code to setup tracing to Application Insights
# from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
# trace.set_tracer_provider(TracerProvider())
# tracer = trace.get_tracer(__name__)
# span_processor = BatchSpanProcessor(
#     AzureMonitorTraceExporter.from_connection_string(
#         os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
#     )
# )
# trace.get_tracer_provider().add_span_processor(span_processor)


def chat_completion_streaming(key, endpoint, model_name):
    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    response = client.complete(
        stream=True,
        messages=[
            SystemMessage(content="You are a helpful assistant."),
            UserMessage(content="Tell me about software engineering in five sentences."),
        ],
        model=model_name,
    )
    for update in response:
        if update.choices:
            print(update.choices[0].delta.content or "", end="")
            pass
    client.close()


# The tracer.start_as_current_span decorator will trace the function call and enable adding additional attributes
# to the span in the function implementation. Note that this will trace the function parameters and their values.
@tracer.start_as_current_span("get_temperature")
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


def get_weather(city: str) -> str:
    if city == "Seattle":
        return "Nice weather"
    elif city == "New York City":
        return "Good weather"
    else:
        return "Unavailable"


def chat_completion_with_function_call(key, endpoint, model_name):
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

    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="What is the weather and temperature in Seattle?"),
    ]

    response = client.complete(messages=messages, model=model_name, tools=[weather_description, temperature_in_city])

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
            response = client.complete(messages=messages, model=model_name, tools=[weather_description, temperature_in_city])
    
    print(f"Model response = {response.choices[0].message.content}")


def main():
    # Setup Azure Core settings to use OpenTelemetry tracing
    settings.tracing_implementation = "OpenTelemetry"

    # Instrument AI Inference API
    AIInferenceApiInstrumentor().instrument()

    # Read AI Inference API configuration
    endpoint = os.environ.get("AZUREAI_ENDPOINT_URL")
    key = os.environ.get("AZUREAI_ENDPOINT_KEY")
    model_name = os.environ.get("AZUREAI_MODEL_NAME")

    print("===== starting chat_completion_streaming() =====")
    chat_completion_streaming(key, endpoint, model_name)
    print("===== chat_completion_streaming() done =====")

    print("===== starting chat_completion_with_function_call() =====")
    chat_completion_with_function_call(key, endpoint, model_name)
    print("===== chat_completion_with_function_call() done =====")
    AIInferenceApiInstrumentor().uninstrument()


if __name__ == "__main__":
    main()
