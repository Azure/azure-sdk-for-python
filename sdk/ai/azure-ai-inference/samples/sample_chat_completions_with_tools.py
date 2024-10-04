# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to do chat completions using a synchronous client,
    with the assistance of tools. In this sample, we use a mock function tool to retrieve
    flight information in order to answer a query about the next flight between two
    cities. Make sure that the AI model you use supports tools.

    This sample assumes the AI model is hosted on a Serverless API or
    Managed Compute endpoint. For GitHub Models or Azure OpenAI endpoints,
    the client constructor needs to be modified. See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#key-concepts

USAGE:
    python sample_chat_completions_with_tools.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
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
        ChatCompletionsToolDefinition,
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

    # Create a chat completion client. Make sure you selected a model that supports tools.
    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    # Make a chat completions call asking for flight information, while providing a tool to handle the request
    messages = [
        SystemMessage(content="You an assistant that helps users find flight information."),
        UserMessage(content="What is the next flights from Seattle to Miami?"),
    ]

    response = client.complete(
        messages=messages,
        tools=[flight_info],
    )

    # Note that in the above call we did not specify `tool_choice`. The service defaults to a setting equivalent
    # to specifying `tool_choice=ChatCompletionsToolChoicePreset.AUTO`. Other than ChatCompletionsToolChoicePreset
    # options, you can also explicitly force the model to use a function tool by specifying:
    # tool_choice=ChatCompletionsNamedToolChoice(function=ChatCompletionsNamedToolChoiceFunction(name="get_flight_info"))

    # The model should be asking for a tool call
    if response.choices[0].finish_reason == CompletionsFinishReason.TOOL_CALLS:

        # Append the previous model response to the chat history
        messages.append(AssistantMessage(tool_calls=response.choices[0].message.tool_calls))

        # In this sample we assume only one tool call was requested
        if response.choices[0].message.tool_calls is not None and len(response.choices[0].message.tool_calls) == 1:

            tool_call = response.choices[0].message.tool_calls[0]

            # Only tools of type function are supported. Make a function call.
            function_args = json.loads(tool_call.function.arguments.replace("'", '"'))
            print(f"Calling function `{tool_call.function.name}` with arguments {function_args}.")
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
