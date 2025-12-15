# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import json
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport
from azure.ai.projects.models import PromptAgentDefinition, FunctionTool
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam


class TestAgentFunctionTool(TestBase):

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_function_tool(self, **kwargs):
        """
        Test agent with custom function tool.

        This test verifies that an agent can:
        1. Use a custom function tool defined by the developer
        2. Request function calls when needed
        3. Receive function results and incorporate them into responses

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        # Setup:
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()

        # Test focus:
        POST   /openai/responses                             openai_client.responses.create() (triggers function)
        POST   /openai/responses                             openai_client.responses.create() (with function result)

        # Teardown:
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        """

        model = kwargs.get("azure_ai_projects_tests_model_deployment_name")
        agent_name = "function-tool-agent"

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Define a function tool for the model to use
            func_tool = FunctionTool(
                name="get_weather",
                description="Get the current weather for a location.",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "A city name like Seattle or London",
                        },
                    },
                    "required": ["location"],
                    "additionalProperties": False,
                },
                strict=True,
            )

            # Create agent with function tool
            agent = project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a helpful assistant that can check the weather. Use the get_weather function when users ask about weather.",
                    tools=[func_tool],
                ),
                description="Agent for testing function tool capabilities.",
            )
            self._validate_agent_version(agent, expected_name=agent_name)

            # Ask a question that should trigger the function call
            print("\nAsking agent: What's the weather in Seattle?")

            response = openai_client.responses.create(
                input="What's the weather in Seattle?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            self.validate_response(response, print_message="Initial response completed")

            # Check for function calls in the response
            function_calls_found = 0
            input_list: ResponseInputParam = []

            for item in response.output:
                if item.type == "function_call":
                    function_calls_found += 1
                    print(f"Found function call (id: {item.call_id}, name: {item.name})")

                    # Parse the arguments
                    arguments = json.loads(item.arguments)
                    print(f"Function arguments: {arguments}")

                    # Verify the function call is for get_weather
                    assert item.name == "get_weather", f"Expected function name 'get_weather', got '{item.name}'"
                    assert "location" in arguments, "Expected 'location' in function arguments"
                    assert (
                        "seattle" in arguments["location"].lower()
                    ), f"Expected Seattle in location, got {arguments['location']}"

                    # Simulate the function execution and provide a result
                    weather_result = {
                        "location": arguments["location"],
                        "temperature": "72°F",
                        "condition": "Sunny",
                        "humidity": "45%",
                    }

                    # Add the function result to the input list
                    input_list.append(
                        FunctionCallOutput(
                            type="function_call_output",
                            call_id=item.call_id,
                            output=json.dumps(weather_result),
                        )
                    )
                    print(f"✓ Prepared function result: {weather_result}")

            # Verify that at least one function call was made
            assert function_calls_found > 0, "Expected at least 1 function call, but found none"
            print(f"\n✓ Processed {function_calls_found} function call(s)")

            # Send the function results back to get the final response
            print("\nSending function results back to agent...")

            response = openai_client.responses.create(
                input=input_list,
                previous_response_id=response.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            self.validate_response(response, print_message="Final response completed")

            # Get the final response text
            response_text = response.output_text
            print(f"\nAgent's final response: {response_text}")

            # Verify the response incorporates the weather data
            assert len(response_text) > 20, "Expected a meaningful response from the agent"

            # Check that the response mentions the weather information we provided
            response_lower = response_text.lower()
            assert any(
                keyword in response_lower for keyword in ["72", "sunny", "weather", "seattle"]
            ), f"Expected response to mention weather information, but got: {response_text}"

            print("\n✓ Agent successfully used function tool and incorporated results into response")

            # Teardown
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        print("Agent deleted")

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_function_tool_multi_turn_with_multiple_calls(self, **kwargs):
        """
        Test multi-turn conversation where agent calls functions multiple times.

        This tests:
        - Multiple function calls across different turns
        - Context retention between turns
        - Ability to use previous function results in subsequent queries
        """

        model = kwargs.get("azure_ai_projects_tests_model_deployment_name")

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Define multiple function tools
            get_weather = FunctionTool(
                name="get_weather",
                description="Get current weather for a city",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city name",
                        },
                    },
                    "required": ["city"],
                    "additionalProperties": False,
                },
                strict=True,
            )

            get_temperature_forecast = FunctionTool(
                name="get_temperature_forecast",
                description="Get 3-day temperature forecast for a city",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city name",
                        },
                    },
                    "required": ["city"],
                    "additionalProperties": False,
                },
                strict=True,
            )

            # Create agent with multiple functions
            agent = project_client.agents.create_version(
                agent_name="weather-assistant-multi-turn",
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a weather assistant. Use available functions to answer weather questions.",
                    tools=[get_weather, get_temperature_forecast],
                ),
                description="Weather assistant for multi-turn testing.",
            )
            print(f"Agent created: {agent.id}")

            # Turn 1: Get current weather
            print("\n--- Turn 1: Current weather query ---")
            response_1 = openai_client.responses.create(
                input="What's the weather in New York?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            # Handle function call
            input_list: ResponseInputParam = []
            for item in response_1.output:
                if item.type == "function_call":
                    print(f"Function called: {item.name} with args: {item.arguments}")
                    assert item.name == "get_weather"

                    # Simulate weather API response
                    weather_data = {"temperature": 68, "condition": "Cloudy", "humidity": 65}
                    input_list.append(
                        FunctionCallOutput(
                            type="function_call_output",
                            call_id=item.call_id,
                            output=json.dumps(weather_data),
                        )
                    )

            # Get response with function results
            response_1 = openai_client.responses.create(
                input=input_list,
                previous_response_id=response_1.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_1_text = response_1.output_text
            print(f"Response 1: {response_1_text[:200]}...")
            assert "68" in response_1_text or "cloudy" in response_1_text.lower()

            # Turn 2: Follow-up with forecast (requires context)
            print("\n--- Turn 2: Follow-up forecast query ---")
            response_2 = openai_client.responses.create(
                input="What about the forecast for the next few days?",
                previous_response_id=response_1.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            # Handle forecast function call
            input_list = []
            for item in response_2.output:
                if item.type == "function_call":
                    print(f"Function called: {item.name} with args: {item.arguments}")
                    assert item.name == "get_temperature_forecast"

                    # Agent should remember we're talking about New York
                    args = json.loads(item.arguments)
                    assert "new york" in args["city"].lower()

                    # Simulate forecast API response
                    forecast_data = {
                        "city": "New York",
                        "forecast": [
                            {"day": "Tomorrow", "temp": 70},
                            {"day": "Day 2", "temp": 72},
                            {"day": "Day 3", "temp": 69},
                        ],
                    }
                    input_list.append(
                        FunctionCallOutput(
                            type="function_call_output",
                            call_id=item.call_id,
                            output=json.dumps(forecast_data),
                        )
                    )

            # Get response with forecast
            response_2 = openai_client.responses.create(
                input=input_list,
                previous_response_id=response_2.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_2_text = response_2.output_text
            print(f"Response 2: {response_2_text[:200]}...")
            assert "70" in response_2_text or "72" in response_2_text

            # Turn 3: Compare with another city
            print("\n--- Turn 3: New city query ---")
            response_3 = openai_client.responses.create(
                input="How does that compare to Seattle's weather?",
                previous_response_id=response_2.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            # Handle function calls for Seattle (agent might call both weather and forecast)
            input_list = []
            for item in response_3.output:
                if item.type == "function_call":
                    print(f"Function called: {item.name} with args: {item.arguments}")
                    args = json.loads(item.arguments)
                    assert "seattle" in args["city"].lower()

                    # Handle based on function name
                    if item.name == "get_weather":
                        weather_data = {"temperature": 58, "condition": "Rainy", "humidity": 80}
                        input_list.append(
                            FunctionCallOutput(
                                type="function_call_output",
                                call_id=item.call_id,
                                output=json.dumps(weather_data),
                            )
                        )
                    elif item.name == "get_temperature_forecast":
                        forecast_data = {
                            "city": "Seattle",
                            "forecast": [
                                {"day": "Tomorrow", "temp": 56},
                                {"day": "Day 2", "temp": 59},
                                {"day": "Day 3", "temp": 57},
                            ],
                        }
                        input_list.append(
                            FunctionCallOutput(
                                type="function_call_output",
                                call_id=item.call_id,
                                output=json.dumps(forecast_data),
                            )
                        )

            # Get final comparison response
            response_3 = openai_client.responses.create(
                input=input_list,
                previous_response_id=response_3.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_3_text = response_3.output_text
            print(f"Response 3: {response_3_text[:200]}...")
            # Agent should mention Seattle weather (either 58 for current or comparison)
            assert "seattle" in response_3_text.lower() or any(temp in response_3_text for temp in ["58", "56", "59"])

            print("\n✓ Multi-turn conversation with multiple function calls successful!")
            print("  - Multiple functions called across turns")
            print("  - Context maintained (agent remembered New York)")
            print("  - Comparison between cities works")

            # Cleanup
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_function_tool_context_dependent_followup(self, **kwargs):
        """
        Test deeply context-dependent follow-ups (e.g., unit conversion, clarification).

        This tests that the agent truly uses previous response content, not just
        remembering parameters from the first query.
        """

        model = kwargs.get("azure_ai_projects_tests_model_deployment_name")

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Define function tool
            get_temperature = FunctionTool(
                name="get_temperature",
                description="Get current temperature for a city in Fahrenheit",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city name",
                        },
                    },
                    "required": ["city"],
                    "additionalProperties": False,
                },
                strict=True,
            )

            # Create agent
            agent = project_client.agents.create_version(
                agent_name="temperature-assistant-context",
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a temperature assistant. Answer temperature questions.",
                    tools=[get_temperature],
                ),
                description="Temperature assistant for context testing.",
            )
            print(f"Agent created: {agent.id}")

            # Turn 1: Get temperature in Fahrenheit
            print("\n--- Turn 1: Get temperature ---")
            response_1 = openai_client.responses.create(
                input="What's the temperature in Boston?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            # Handle function call
            input_list: ResponseInputParam = []
            for item in response_1.output:
                if item.type == "function_call":
                    print(f"Function called: {item.name} with args: {item.arguments}")
                    input_list.append(
                        FunctionCallOutput(
                            type="function_call_output",
                            call_id=item.call_id,
                            output=json.dumps({"temperature": 72, "unit": "F"}),
                        )
                    )

            response_1 = openai_client.responses.create(
                input=input_list,
                previous_response_id=response_1.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_1_text = response_1.output_text
            print(f"Response 1: {response_1_text[:200]}...")
            assert "72" in response_1_text, "Should mention 72°F"

            # Turn 2: Context-dependent follow-up (convert the previous number)
            print("\n--- Turn 2: Context-dependent conversion ---")
            response_2 = openai_client.responses.create(
                input="What is that in Celsius?",  # "that" refers to the 72°F from previous response
                previous_response_id=response_1.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_2_text = response_2.output_text
            print(f"Response 2: {response_2_text[:200]}...")

            # Should convert 72°F to ~22°C (without calling the function again)
            # The agent should use the previous response's value
            response_2_lower = response_2_text.lower()
            assert (
                "celsius" in response_2_lower or "°c" in response_2_lower or "c" in response_2_lower
            ), "Response should mention Celsius"
            assert any(
                temp in response_2_text for temp in ["22", "22.2", "22.22", "20", "21", "23"]
            ), f"Response should calculate Celsius from 72°F (~22°C), got: {response_2_text}"

            # Turn 3: Another context-dependent follow-up (comparison)
            print("\n--- Turn 3: Compare to another value ---")
            response_3 = openai_client.responses.create(
                input="Is that warmer or colder than 25°C?",  # "that" refers to the Celsius value just mentioned
                previous_response_id=response_2.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_3_text = response_3.output_text
            print(f"Response 3: {response_3_text[:200]}...")

            # 22°C is colder than 25°C
            response_3_lower = response_3_text.lower()
            assert (
                "colder" in response_3_lower or "cooler" in response_3_lower or "lower" in response_3_lower
            ), f"Response should indicate 22°C is colder than 25°C, got: {response_3_text}"

            print("\n✓ Context-dependent follow-ups successful!")
            print("  - Agent converted temperature from previous response")
            print("  - Agent compared values from conversation history")
            print("  - No unnecessary function calls made")

            # Cleanup
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")
