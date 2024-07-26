# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to do chat completions using a synchronous client,
    with the assistance of tools. In this sample, we use a mock function tool to retrieve
    flight information in order to answer a query about the next flight between two
    cities.

USAGE:
    python sample_chat_completions_with_tools.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_CHAT_KEY - Your model key (a 32-character string). Keep it secret.
"""


def sample_chat_completions_with_tools():
    import os
    import json

    try:
        endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
        key = os.environ["AZURE_AI_CHAT_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_CHAT_ENDPOINT' or 'AZURE_AI_CHAT_KEY'")
        print("Set them before running this sample.")
        exit()

    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import (
        AssistantMessage,
        ChatCompletionsFunctionToolCall,
        ChatCompletionsFunctionToolDefinition,
        CompletionsFinishReason,
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
        str: The airline name, fight number, date and time of the next flight between the cities.
        """
        if origin_city == "Seattle" and destination_city == "Miami":
            return "Delta airlines flight number 123 from Seattle to Miami, departing May 7th, 2024 at 10:00 AM."
        else:
            return "Sorry, I don't have that information."

    # Define a 'tool' that the model can use to retrieves flight information
    flight_info = ChatCompletionsFunctionToolDefinition(
        function=FunctionDefinition(
            name="get_flight_info",
            description="Returns information about the next flight between two cities. This includes the name of the airline, flight number and the date and time of the next flight",
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

    # Create a chat completion client. Make sure you selected a model that supports tools.
    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Make a chat completions call asking for flight information, while providing a tool to handle the request
    messages = [
        SystemMessage(content="You an assistant that helps users find flight information."),
        UserMessage(content="What is the next flights from Seattle to Miami?"),
    ]

    response = client.complete(
        messages=messages,
        tools=[flight_info],
    )

    # The model should be asking for tool calls
    if response.choices[0].finish_reason == CompletionsFinishReason.TOOL_CALLS:

        # Append the previous model response to the chat history
        messages.append(AssistantMessage(tool_calls=response.choices[0].message.tool_calls))

        # The tool should be of type function call. He we assume only one function call is required.
        if response.choices[0].message.tool_calls is not None and len(response.choices[0].message.tool_calls) == 1:

            tool_call = response.choices[0].message.tool_calls[0]

            if type(tool_call) is ChatCompletionsFunctionToolCall:

                function_args = json.loads(tool_call.function.arguments.replace("'", '"'))
                print(f"Calling function `{tool_call.function.name}` with arguments {function_args}")
                callable_func = locals()[tool_call.function.name]

                function_response = callable_func(**function_args)
                print(f"Function response = {function_response}")

                # Provide the tool response to the model, by appending it to the chat history
                messages.append(ToolMessage(tool_call_id=tool_call.id, content=function_response))

                # With the additional tools information on hand, get another response from the model
                response = client.complete(messages=messages, tools=[flight_info])

                print(f"Model response = {response.choices[0].message.content}")


if __name__ == "__main__":
    sample_chat_completions_with_tools()
