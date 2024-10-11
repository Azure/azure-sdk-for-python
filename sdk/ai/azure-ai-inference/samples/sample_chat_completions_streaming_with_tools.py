# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to do chat completions using a synchronous client,
    with the assistance of tools, with streaming service response. In this sample,
    we use a mock function tool to retrieve flight information in order to answer
    a query about the next flight between two cities. Make sure that the AI model
    you use supports tools. The sample supports either Serverless API endpoint /
    Managed Compute endpoint, or Azure OpenAI endpoint. Set the boolean variable
    `use_azure_openai_endpoint` to select between the two. API key authentication
    is used for both endpoints in this sample.

USAGE:
    python sample_chat_completions_streaming_with_tools.py

    For use_azure_openai_endpoint = True, set these two environment variables before running the sample:
    1) AZURE_OPENAI_CHAT_ENDPOINT - Your AOAI endpoint URL, with partial path, in the form
        https://<your-unique-resouce-name>.openai.azure.com/openai/deployments/<your-deployment-name>
        where `your-unique-resource-name` is your globally unique AOAI resource name,
        and `your-deployment-name` is your AI Model deployment name.
        For example: https://your-unique-host.openai.azure.com/openai/deployments/gpt-4o
    2) AZURE_OPENAI_CHAT_KEY - Your model key (a 32-character string). Keep it secret.

    For use_azure_openai_endpoint = False, set these two environment variables before running the sample:
    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_CHAT_KEY - Your model key (a 32-character string). Keep it secret.
"""
import sys

use_azure_openai_endpoint = True

def sample_chat_completions_streaming_with_tools():
    import os
    import json

    try:
        if use_azure_openai_endpoint:
            endpoint = os.environ["AZURE_OPENAI_CHAT_ENDPOINT"]
            key = os.environ["AZURE_OPENAI_CHAT_KEY"]
        else:
            endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
            key = os.environ["AZURE_AI_CHAT_KEY"]

    except KeyError:
        print("Missing environment variable 'AZURE_AI_CHAT_ENDPOINT' or 'AZURE_AI_CHAT_KEY'")
        print("Set them before running this sample.")
        exit()

    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import (
        AssistantMessage,
        ChatCompletionsToolCall,
        ChatCompletionsToolDefinition,
        FunctionCall,
        FunctionDefinition,
        SystemMessage,
        ToolMessage,
        UserMessage,
    )
    from azure.core.credentials import AzureKeyCredential

    # Define a function that retrieves flight information
    def get_flight_info(origin_city: str, destination_city: str):
        """
        This is a mock function that returns information about the next
        flight between two cities.

        Parameters:
        origin_city (str): The name of the city where the flight originates.
        destination_city (str): The destination city.

        Returns:
        str: The airline name, fight number, date and time of the next flight between the cities, in JSON format.
        """
        if origin_city == "Seattle" and destination_city == "Miami":
            return json.dumps({
                "airline": "Delta",
                "flight_number": "DL123",
                "flight_date": "May 7th, 2024",
                "flight_time": "10:00AM"})
        return json.dumps({"error": "No flights found between the cities"})

    # Define a function 'tool' that the model can use to retrieves flight information
    flight_info = ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            name="get_flight_info",
            description="Returns information about the next flight between two cities. This includes the name of the airline, flight number and the date and time of the next flight, in JSON format.",
            parameters={
                "type": "object",
                "properties": {
                    "origin_city": {
                        "type": "string",
                        "description": "The name of the city where the flight originates",
                    },
                    "destination_city": {
                        "type": "string",
                        "description": "The flight destination city",
                    },
                },
                "required": ["origin_city", "destination_city"],
            },
        )
    )

    if use_azure_openai_endpoint:
        # Create a chat completion client for Azure OpenAI endpoint
        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(""),  # Pass in an empty value
            headers={"api-key": key},
            api_version="2024-06-01",  # AOAI api-version. Update as needed.
        )
    else:
        # Create a chat completions client for Serverless API endpoint or Managed Compute endpoint
        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )

    # Make a streaming chat completions call asking for flight information, while providing a tool to handle the request
    messages = [
        SystemMessage(content="You an assistant that helps users find flight information."),
        UserMessage(content="What is the next flights from Seattle to Miami?"),
    ]

    response = client.complete(
        messages=messages,
        tools=[flight_info],
        stream=True)

    # Note that in the above call we did not specify `tool_choice`. The service defaults to a setting equivalent
    # to specifying `tool_choice=ChatCompletionsToolChoicePreset.AUTO`. Other than ChatCompletionsToolChoicePreset
    # options, you can also explicitly force the model to use a function tool by specifying:
    # tool_choice=ChatCompletionsNamedToolChoice(function=ChatCompletionsNamedToolChoiceFunction(name="get_flight_info"))

    # At this point we expect a function tool call in the model response
    tool_call_id: str = ""
    function_name: str = ""
    function_args: str = ""
    for update in response:
        # Detect a function tool call in the model response,
        # get the function name, id, and concatenate the function-call arguments
        # since they may be streamed across multiple updates.
        if update.choices[0].delta.tool_calls is not None:
            if update.choices[0].delta.tool_calls[0].function.name is not None:
                function_name = update.choices[0].delta.tool_calls[0].function.name
            if update.choices[0].delta.tool_calls[0].id is not None:
                tool_call_id = update.choices[0].delta.tool_calls[0].id
            function_args += update.choices[0].delta.tool_calls[0].function.arguments or ""

    # Append the previous model response to the chat history
    messages.append(
        AssistantMessage(
            tool_calls=[
                ChatCompletionsToolCall(
                    id=tool_call_id,
                    function=FunctionCall(
                        name=function_name,
                        arguments=function_args
                    )
                )
            ]
        )
    )

    # Make the function call
    print(f"Calling function `{function_name}` with arguments {function_args}.")
    callable_func = locals()[function_name]
    function_args_mapping = json.loads(function_args.replace("'", '"'))
    function_response = callable_func(**function_args_mapping)
    print(f"Function response = {function_response}")

    # Append the function response as a tool message to the chat history
    messages.append(
        ToolMessage(
            tool_call_id=tool_call_id,
            content=function_response
        )
    )

    # With the additional tools information on hand, get another streaming response from the model
    response = client.complete(
        messages=messages,
        tools=[flight_info],
        stream=True
    )

    print("Model response = ", end="")
    for update in response:
        print(update.choices[0].delta.content or "", end="", flush=True)

    client.close()


if __name__ == "__main__":
    sample_chat_completions_streaming_with_tools()
