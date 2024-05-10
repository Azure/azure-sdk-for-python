# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
NOTE: 
    This sample is still work in progress...

DESCRIPTION:
    This sample demonstrates how to do chat completions using a synchronous client,
    with the assistance of tools. In this sample, we use a mock function tool to retrieve
    flight information in order to answer a query about the next flight between two
    cities.

USAGE:
    python sample_chat_completions_with_tools.py

    Set these two environment variables before running the sample:
    1) CHAT_COMPLETIONS_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) CHAT_COMPLETIONS_KEY - Your model key (a 32-character string). Keep it secret.
"""


def sample_chat_completions_with_tools():
    import os
    import json

    # Enable unredacted logging, including full request and response payloads (delete me!)
    import sys
    import logging
    logger = logging.getLogger("azure")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    try:
        endpoint = os.environ["CHAT_COMPLETIONS_ENDPOINT"]
        key = os.environ["CHAT_COMPLETIONS_KEY"]
    except KeyError:
        print("Missing environment variable 'CHAT_COMPLETIONS_ENDPOINT' or 'CHAT_COMPLETIONS_KEY'")
        print("Set them before running this sample.")
        exit()

    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import (
        AssistantMessage,
        ChatCompletionsFunctionToolCall,
        ChatCompletionsFunctionToolDefinition,
        ChatCompletionsNamedToolSelection,
        ChatCompletionsToolSelectionPreset,
        CompletionsFinishReason,
        FunctionDefinition,
        SystemMessage,
        ToolMessage,
        UserMessage,
    )
    from azure.core.credentials import AzureKeyCredential

    # Create a chat completion client. Make sure you selected a model that supports tools.
    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key), logging_enable=True)

    # Define a function that retrieves flight information
    def get_flight_info(origin_city: str, destination_city: str):
        """
        This is a mock function that returns information about the next
        flight between two cities.

        Parameters:
        origin_city (str): The name of the city where the flight originates
        destination_city (str): The destination city

        Returns:
        str: The airline name, fight number, date and time of the next flight between the cities
        """
        if origin_city == "Seattle" and destination_city == "Miami":
            return "Delta airlines flight number 123 from Seattle to Miami, departing May 7th, 2024 at 10:00 AM."
            #return '{"info": "Delta airlines flight number 123 from Seattle to Miami, departing May 7th, 2024 at 10:00 AM."}'
        elif origin_city == "Seattle" and destination_city == "Orlando":
            return "American Airlines flight number 456 from Seattle to Orlando, departing May 8th, 2024 at 2:45 PM."
            #return '{"info": "American Airlines flight number 456 from Seattle to Orlando, departing May 8th, 2024 at 2:45 PM."}'
        else:
            return "I don't have that information."
            #return '{"into": "I don\'t have that information."}'

    # Define a 'tool' that the model can use to retrieves flight information
    flight_info = ChatCompletionsFunctionToolDefinition(
        function=FunctionDefinition(
            name="get_flight_info",
            description="Returns information about the next flight between two cities. This inclues the name of the airline, flight number and the date and time of the next flight",
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

    # Make a chat completions call asking for flight information, while providing a tool to handle the request
    messages = [
        SystemMessage(content="You an assistant that helps users find flight information."),
        UserMessage(content="What are the next flights from Seattle to Miami and from Seattle to Orlando?"),
    ]

    result = client.create(
        messages=messages,
        tools=[flight_info],
        #tool_choice=ChatCompletionsNamedToolSelection(type="function")  # Cohere model does not support
    )

    # As long as the model keeps requesting tool calls, make tool calls and provide the tool outputs to the model
    while result.choices[0].finish_reason == CompletionsFinishReason.TOOL_CALLS:

        # Append the previous model response to the chat history
        if result.choices[0].message.tool_calls is not None:
            # TODO: Remove the need to set content=""
            messages.append(AssistantMessage(content="", tool_calls=result.choices[0].message.tool_calls)) 

        # Make new function call(s) as needed. If parallel function calling is supported by the model,
        # we may have more than one tool call request.
        if result.choices[0].message.tool_calls is not None:
            for tool_call in result.choices[0].message.tool_calls:
                if hasattr(tool_call, "function"):
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments.replace("'", '"'))
                    tool_call_id = tool_call.id
                    print(f"Calling function `{function_name}` with arguments {function_args}")
                    callable_func = locals()[function_name]
                    function_response = callable_func(**function_args)
                    print(f"Function response is: {function_response}")

                    # Provide the tool response to the model, by appending it to the chat history
                    messages.append(
                        ToolMessage(tool_call_id=tool_call_id, content=function_response)  # json.dumps(function_response)
                    )

        # With the additional tools information on hand, get another response from the model
        result = client.create(
            messages=messages,
            tools=[flight_info],
            tool_choice=ChatCompletionsToolSelectionPreset.AUTO
        )

    # Print the final response
    print(result.choices[0].message.content)


if __name__ == "__main__":
    sample_chat_completions_with_tools()
