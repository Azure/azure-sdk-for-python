# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Iterator, List, MutableMapping, Optional, Dict

import json
import os
import pytest
from unittest.mock import MagicMock, Mock, patch

from azure.ai.agents import AgentsClient
from azure.ai.agents.operations import RunsOperations
from azure.ai.agents.models import (
    CodeInterpreterTool,
    FunctionTool,
    RequiredFunctionToolCall,
    RequiredFunctionToolCallDetails,
    RequiredToolCall,
    RunStatus,
    SubmitToolOutputsAction,
    SubmitToolOutputsDetails,
    ToolSet,
    ToolOutput,
    AgentEventHandler,
    ThreadRun,
)

from user_functions import user_functions


JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object


def read_file(file_name: str) -> str:
    with open(os.path.join(os.path.dirname(__file__), "assets", f"{file_name}.txt"), "r") as file:
        return file.read()


main_stream_response = read_file("main_stream_response")
fetch_current_datetime_and_weather_stream_response = read_file("fetch_current_datetime_and_weather_stream_response")
send_email_stream_response = read_file("send_email_stream_response")


def convert_to_byte_iterator(main_stream_response: str) -> Iterator[bytes]:
    yield main_stream_response.encode()


def function1():
    return "output from the first agent"


def function2():
    return "output from the second agent"


def function_throw_exception():
    raise ValueError("Just a minute")


def _read_file(file_name: str) -> str:
    with open(os.path.join(os.path.dirname(__file__), "assets", f"{file_name}.txt"), "r") as file:
        return file.read()


def _convert_to_byte_iterator(input: str) -> Iterator[bytes]:
    yield input.encode()


def _get_stream_with_tool_calls() -> Iterator[bytes]:
    fetch_current_datetime_and_weather_stream_response = _read_file(
        "fetch_current_datetime_and_weather_stream_response"
    )
    return _convert_to_byte_iterator(fetch_current_datetime_and_weather_stream_response)


class TestAgentsMock:
    """Tests for agent operations"""

    LOCAL_FN = {function1.__name__: function1, function2.__name__: function2}

    def get_mock_client(self) -> AgentsClient:
        """Return the fake project client"""
        client = AgentsClient(
            endpoint="www.bcac95dd-a1eb-11ef-978f-8c1645fec84b.com",
            credential=MagicMock(),
        )
        client.runs.submit_tool_outputs = MagicMock()
        return client

    def get_toolset(self, file_id: Optional[str], function: Optional[str]) -> Optional[ToolSet]:
        """Get the tool set with given file id and function"""
        if file_id is None or function is None:
            return None
        functions = FunctionTool({function})
        code_interpreter = CodeInterpreterTool(file_ids=[file_id])
        toolset = ToolSet()
        toolset.add(functions)
        toolset.add(code_interpreter)
        return toolset

    def _assert_pipeline_and_reset(self, mock_pipeline_run: MagicMock, tool_set: Optional[ToolSet]) -> None:
        """Check that the pipeline has correct values of tools."""
        mock_pipeline_run.assert_called_once()
        data = json.loads(mock_pipeline_run.call_args_list[0].args[0].body)
        assert isinstance(data, dict), f"Wrong body JSON type expected dict, found {type(data)}"
        if tool_set is not None:
            assert "tool_resources" in data, "tool_resources must be in data"
            assert "tools" in data, "tools must be in data"
            expected_file_id = tool_set.resources.code_interpreter.file_ids[0]
            expected_function_name = tool_set.definitions[0].function.name
            # Check code interpreter file id.
            assert data["tool_resources"], "Tools resources is empty."
            assert "code_interpreter" in data["tool_resources"]
            assert data["tool_resources"]["code_interpreter"], "Code interpreter section is empty."
            assert "file_ids" in data["tool_resources"]["code_interpreter"]
            assert (
                data["tool_resources"]["code_interpreter"]["file_ids"][0] == expected_file_id
            ), f"{expected_file_id[0]=}, but found {data['tool_resources']['code_interpreter']['file_ids']}"
            # Check tools.
            assert data["tools"], "Tools must not be empty"
            assert "function" in data["tools"][0]
            assert "name" in data["tools"][0]["function"]
            assert (
                data["tools"][0]["function"]["name"] == expected_function_name
            ), f"{expected_function_name=}, but encountered {data['tools'][0]['function']['name']}"
        else:
            assert "tool_resources" not in data, "tool_resources must not be in data"
            assert "tools" not in data, "tools must not be in data"
        mock_pipeline_run.reset_mock()

    def _get_agent_json(self, name: str, agent_id: str, tool_set: Optional[ToolSet]) -> Dict[str, Any]:
        """Read in the agent JSON, so that we can assume service returnred it."""
        with open(
            os.path.join(os.path.dirname(__file__), "test_data", "agent.json"),
            "r",
        ) as fp:
            agent_dict: Dict[str, Any] = json.load(fp)
        assert isinstance(agent_dict, dict)
        agent_dict["name"] = name
        agent_dict["id"] = agent_id
        if tool_set is not None:
            agent_dict["tool_resources"] = tool_set.resources.as_dict()
            agent_dict["tools"] = tool_set.definitions
        return agent_dict

    def _get_run(
        self, thread_id: str, tool_set: Optional[ToolSet], add_azure_fn: bool = False, is_complete: bool = False
    ) -> Dict[str, Any]:
        """Return JSON as if we have created the run."""
        with open(
            os.path.join(
                os.path.dirname(__file__),
                "test_data",
                "thread_run.json",
            ),
            "r",
        ) as fp:
            run_dict: Dict[str, Any] = json.load(fp)
        run_dict["id"] = thread_id
        run_dict["assistant_id"] = thread_id[3:]
        assert isinstance(run_dict, dict)
        if is_complete:
            run_dict["status"] = RunStatus.COMPLETED
        tool_calls = []
        definitions = []
        if add_azure_fn:
            tool_calls.append(RequiredToolCall(id="1", type="azure_function"))
            definitions.append(
                {
                    "type": "azure_function",
                    "azure_function": {
                        "function": {
                            "name": "foo",
                            "description": "Get answers from the foo bot.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "The question to ask."},
                                    "outputqueueuri": {"type": "string", "description": "The full output queue uri."},
                                },
                                "required": ["query"],
                            },
                        },
                        "input_binding": {
                            "type": "storage_queue",
                            "storage_queue": {
                                "queue_service_uri": "https://example.windows.net",
                                "queue_name": "azure-function-foo-input",
                            },
                        },
                        "output_binding": {
                            "type": "storage_queue",
                            "storage_queue": {
                                "queue_service_uri": "https://example.queue.core.windows.net",
                                "queue_name": "azure-function-tool-output",
                            },
                        },
                    },
                }
            )
        if tool_set is not None:
            tool_calls.append(
                RequiredFunctionToolCall(
                    id="0",
                    function=RequiredFunctionToolCallDetails(
                        name=tool_set.definitions[0].function.name,
                        arguments="{}",
                    ),
                )
            )
            definitions.extend(tool_set.definitions)
            run_dict["tool_resources"] = tool_set.resources.as_dict()
        if tool_calls:
            sb = SubmitToolOutputsAction(submit_tool_outputs=SubmitToolOutputsDetails(tool_calls=tool_calls))
            run_dict["required_action"] = sb.as_dict()
            run_dict["tools"] = definitions
        return run_dict

    def _assert_tool_call(self, submit_tool_mock: MagicMock, run_id: str, tool_set: Optional[ToolSet]) -> None:
        """Check that submit_tool_outputs_to_run was called with correct parameters or was not called"""
        if tool_set is not None:
            expected_out = TestAgentsMock.LOCAL_FN[tool_set.definitions[0].function.name]()
            submit_tool_mock.assert_called_once()
            submit_tool_mock.assert_called_with(
                thread_id="some_thread_id",
                run_id=run_id,
                tool_outputs=[{"tool_call_id": "0", "output": expected_out}],
            )
            submit_tool_mock.reset_mock()
        else:
            submit_tool_mock.assert_not_called()

    def _set_toolcalls(
        self, agents_client: AgentsClient, toolset1: Optional[ToolSet], toolset2: Optional[ToolSet]
    ) -> None:
        """Set the tool calls for the agent."""
        max_retry = 3
        if toolset1 and toolset2:
            function_in_toolset1 = set(toolset1.get_tool(tool_type=FunctionTool)._functions.values())
            function_in_toolset2 = set(toolset2.get_tool(tool_type=FunctionTool)._functions.values())
            function_tool = FunctionTool(function_in_toolset1)
            function_tool.add_functions(function_in_toolset2)
            agents_client.enable_auto_function_calls(function_tool, max_retry=max_retry)
        elif toolset1:
            agents_client.enable_auto_function_calls(toolset1, max_retry=max_retry)
        elif toolset2:
            agents_client.enable_auto_function_calls(toolset2, max_retry=max_retry)

    @patch("azure.ai.agents._client.PipelineClient")
    @pytest.mark.parametrize(
        "file_agent_1,file_agent_2",
        [
            ("file_for_agent1", "file_for_agent2"),
            (None, "file_for_agent2"),
            ("file_for_agent1", None),
            (None, None),
        ],
    )
    def test_multiple_agents_create(
        self,
        mock_pipeline_client_gen: MagicMock,
        file_agent_1: Optional[str],
        file_agent_2: Optional[str],
    ) -> None:
        """Test agents can get correct toolset."""
        toolset1 = self.get_toolset(file_agent_1, function1)
        toolset2 = self.get_toolset(file_agent_2, function2)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            self._get_agent_json("first", "123", toolset1),
            self._get_agent_json("second", "456", toolset2),
            self._get_run("run123", toolset1),  # create_run
            self._get_run("run123", toolset1),  # get_run
            self._get_run("run123", toolset1, is_complete=True),  # get_run after resubmitting with tool results
            self._get_run("run456", toolset2),  # create_run
            self._get_run("run456", toolset2),  # get_run
            self._get_run("run456", toolset2, is_complete=True),  # get_run after resubmitting with tool results
            "{}",  # delete agent 1
            "{}",  # delete agent 2
        ]
        mock_pipeline_response = MagicMock()
        mock_pipeline_response.http_response = mock_response
        mock_pipeline = MagicMock()
        mock_pipeline._pipeline.run.return_value = mock_pipeline_response
        mock_pipeline_client_gen.return_value = mock_pipeline
        agents_client = self.get_mock_client()
        with agents_client:
            self._set_toolcalls(agents_client, toolset1, toolset2)
            # Check that pipelines are created as expected.
            agent1 = agents_client.create_agent(
                model="gpt-4-1106-preview",
                name="first",
                instructions="You are a helpful agent",
                toolset=toolset1,
            )
            self._assert_pipeline_and_reset(mock_pipeline._pipeline.run, tool_set=toolset1)

            agent2 = agents_client.create_agent(
                model="gpt-4-1106-preview",
                name="second",
                instructions="You are a helpful agent",
                toolset=toolset2,
            )
            self._assert_pipeline_and_reset(mock_pipeline._pipeline.run, tool_set=toolset2)
            # Check that the new agents are called with correct tool sets.
            agents_client.runs.create_and_process(thread_id="some_thread_id", agent_id=agent1.id, polling_interval=0)
            self._assert_tool_call(agents_client.runs.submit_tool_outputs, "run123", toolset1)

            agents_client.runs.create_and_process(thread_id="some_thread_id", agent_id=agent2.id, polling_interval=0)
            self._assert_tool_call(agents_client.runs.submit_tool_outputs, "run456", toolset2)
            # Check that we cleanup tools after deleting agent.
            agents_client.delete_agent(agent1.id)
            agents_client.delete_agent(agent2.id)

    @patch("azure.ai.agents.operations._operations.RunsOperations.cancel")
    @patch("azure.ai.agents._client.PipelineClient")
    def test_auto_function_calls_retry(
        self,
        mock_pipeline_client_gen: MagicMock,
        mock_cancel_run: MagicMock,
    ) -> None:
        """Test azure function with toolset."""
        toolset = self.get_toolset("file_for_agent1", function_throw_exception)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            self._get_agent_json("first", "123", toolset),
            self._get_run("run2", toolset),  # create_run
            self._get_run("run2", toolset),  # get_run
            self._get_run("run3", toolset),  # get_run
            self._get_run("run4", toolset),  # get_run
            self._get_run("run5", toolset),  # get_run
        ]
        mock_pipeline_response = MagicMock()
        mock_pipeline_response.http_response = mock_response
        mock_pipeline = MagicMock()
        mock_pipeline._pipeline.run.return_value = mock_pipeline_response
        mock_pipeline_client_gen.return_value = mock_pipeline
        agents_client = self.get_mock_client()
        with agents_client:
            # Check that pipelines are created as expected.
            self._set_toolcalls(agents_client, toolset, None)
            agent1 = agents_client.create_agent(
                model="gpt-4-1106-preview",
                name="first",
                instructions="You are a helpful assistant",
                toolset=toolset,
            )
            # Create run with new tool set, which also can be none.
            agents_client.runs.create_and_process(thread_id="some_thread_id", agent_id=agent1.id)
            assert mock_cancel_run.call_count == 1
            assert agents_client.runs.submit_tool_outputs.call_count == 3

    @patch("azure.ai.agents.operations._operations.RunsOperations.cancel")
    @patch("azure.ai.agents._client.PipelineClient")
    def test_auto_function_calls_in_stream(
        self,
        mock_pipeline_client_gen: MagicMock,
        mock_cancel_run: MagicMock,
    ) -> None:
        """Test azure function with toolset."""
        toolset = self.get_toolset("file_for_agent1", function_throw_exception)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            self._get_agent_json("first", "123", toolset),
        ]
        mock_cancel_run.return_value = ThreadRun({"id": "1", "status": RunStatus.CANCELLED})

        mock_pipeline_response = MagicMock()
        mock_pipeline_response.http_response = mock_response
        mock_pipeline = MagicMock()
        mock_pipeline._pipeline.run.return_value = mock_pipeline_response
        mock_pipeline_client_gen.return_value = mock_pipeline
        agents_client = self.get_mock_client()
        with agents_client:
            # Check that pipelines are created as expected.
            self._set_toolcalls(agents_client, toolset, None)
            agent1 = agents_client.create_agent(
                model="gpt-4-1106-preview",
                name="first",
                instructions="You are a helpful assistant",
                toolset=toolset,
            )
            # Create run with new tool set, which also can be none.

            mock_response.iter_bytes.side_effect = [
                _get_stream_with_tool_calls(),  # create_run
                _get_stream_with_tool_calls(),  # submit_tool_outputs_to_run
                _get_stream_with_tool_calls(),  # submit_tool_outputs_to_run
                _get_stream_with_tool_calls(),  # submit_tool_outputs_to_run
            ]

            event_handler = AgentEventHandler()
            with agents_client.runs.stream(
                thread_id="some_thread_id", agent_id=agent1.id, event_handler=event_handler
            ) as stream:
                stream.until_done()
            assert mock_cancel_run.call_count == 1
            assert event_handler.current_retry == 4

    @patch("azure.ai.agents._client.PipelineClient")
    @pytest.mark.parametrize(
        "file_agent_1,file_agent_2",
        [
            ("file_for_agent1", "file_for_agent2"),
            (None, "file_for_agent2"),
            ("file_for_agent1", None),
            (None, None),
        ],
    )
    def test_update_agent_tools(
        self,
        mock_pipeline_client_gen: MagicMock,
        file_agent_1: Optional[str],
        file_agent_2: Optional[str],
    ) -> None:
        """Test that tools are properly updated."""
        toolset1 = self.get_toolset(file_agent_1, function1)
        toolset2 = self.get_toolset(file_agent_2, function2)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            self._get_agent_json("first", "123", toolset1),
            self._get_agent_json("first", "123", toolset2),
        ]
        mock_pipeline_response = MagicMock()
        mock_pipeline_response.http_response = mock_response
        mock_pipeline = MagicMock()
        mock_pipeline._pipeline.run.return_value = mock_pipeline_response
        mock_pipeline_client_gen.return_value = mock_pipeline
        agents_client = self.get_mock_client()
        with agents_client:
            # Check that pipelines are created as expected.
            agent1 = agents_client.create_agent(
                model="gpt-4-1106-preview",
                name="first",
                instructions="You are a helpful agent",
                toolset=toolset1,
            )
            agent1 = agents_client.update_agent(agent1.id, toolset=toolset2)
            if toolset2 is None:
                assert agent1.tools == None
            else:
                assert agent1.tools[0].function.name == function2.__name__

    @patch("azure.ai.agents._client.PipelineClient")
    @pytest.mark.parametrize(
        "file_agent_1,file_agent_2",
        [
            ("file_for_agent1", "file_for_agent2"),
            (None, "file_for_agent2"),
            ("file_for_agent1", None),
            (None, None),
        ],
    )
    def test_create_run_tools_override(
        self,
        mock_pipeline_client_gen: MagicMock,
        file_agent_1: Optional[str],
        file_agent_2: Optional[str],
    ) -> None:
        """Test that if user have set tool set in create create_and_process_run method, that tools are used."""
        toolset1 = self.get_toolset(file_agent_1, function1)
        toolset2 = self.get_toolset(file_agent_2, function2)
        mock_response = MagicMock()
        mock_response.status_code = 200
        side_effect = [self._get_agent_json("first", "123", toolset1)]
        if toolset1 is not None or toolset2 is not None:
            toolset = toolset2 if toolset2 is not None else toolset1
            side_effect.append(self._get_run("run123", toolset))  # create_run
            side_effect.append(self._get_run("run123", toolset))  # get_run
            side_effect.append(
                self._get_run("run123", toolset, is_complete=True)
            )  # get_run after resubmitting with tool results
        else:
            side_effect.append(
                self._get_run("run123", None, is_complete=True)
            )  # Run must be marked as completed in this case.
        mock_response.json.side_effect = side_effect
        mock_pipeline_response = MagicMock()
        mock_pipeline_response.http_response = mock_response
        mock_pipeline = MagicMock()
        mock_pipeline._pipeline.run.return_value = mock_pipeline_response
        mock_pipeline_client_gen.return_value = mock_pipeline
        agents_client = self.get_mock_client()
        with agents_client:
            # Check that pipelines are created as expected.
            self._set_toolcalls(agents_client, toolset1, toolset2)
            agent1 = agents_client.create_agent(
                model="gpt-4-1106-preview",
                name="first",
                instructions="You are a helpful agent",
                toolset=toolset1,
            )
            self._assert_pipeline_and_reset(mock_pipeline._pipeline.run, tool_set=toolset1)

            # Create run with new tool set, which also can be none.
            agents_client.runs.create_and_process(
                thread_id="some_thread_id", agent_id=agent1.id, toolset=toolset2, polling_interval=0
            )
            if toolset2 is not None:
                self._assert_tool_call(agents_client.runs.submit_tool_outputs, "run123", toolset2)
            else:
                self._assert_tool_call(agents_client.runs.submit_tool_outputs, "run123", toolset1)

    @patch("azure.ai.agents._client.PipelineClient")
    @pytest.mark.parametrize(
        "file_agent_1,add_azure_fn",
        [
            ("file_for_agent1", True),
            (None, True),
            ("file_for_agent1", False),
            (None, False),
        ],
    )
    def test_with_azure_function(
        self,
        mock_pipeline_client_gen: MagicMock,
        file_agent_1: Optional[str],
        add_azure_fn: bool,
    ) -> None:
        """Test azure function with toolset."""
        toolset = self.get_toolset(file_agent_1, function1)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            self._get_agent_json("first", "123", toolset),
            self._get_run("run123", toolset, add_azure_fn=add_azure_fn),  # create_run
            self._get_run("run123", toolset, add_azure_fn=add_azure_fn),  # get_run
            self._get_run(
                "run123", toolset, add_azure_fn=add_azure_fn, is_complete=True
            ),  # get_run after resubmitting with tool results
        ]
        mock_pipeline_response = MagicMock()
        mock_pipeline_response.http_response = mock_response
        mock_pipeline = MagicMock()
        mock_pipeline._pipeline.run.return_value = mock_pipeline_response
        mock_pipeline_client_gen.return_value = mock_pipeline
        agents_client = self.get_mock_client()
        with agents_client:
            # Check that pipelines are created as expected.
            self._set_toolcalls(agents_client, toolset, None)
            agent1 = agents_client.create_agent(
                model="gpt-4-1106-preview",
                name="first",
                instructions="You are a helpful agent",
                toolset=toolset,
            )
            # Create run with new tool set, which also can be none.
            agents_client.runs.create_and_process(thread_id="some_thread_id", agent_id=agent1.id, polling_interval=0)
            self._assert_tool_call(agents_client.runs.submit_tool_outputs, "run123", toolset)

    def _assert_stream_call(self, submit_tool_mock: MagicMock, run_id: str, tool_set: Optional[ToolSet]) -> None:
        """Assert that stream has received the correct values."""
        if tool_set is not None:
            expected_out = TestAgentsMock.LOCAL_FN[tool_set.definitions[0].function.name]()
            submit_tool_mock.assert_called_once()
            submit_tool_mock.assert_called_with(
                thread_id="some_thread_id",
                run_id=run_id,
                tool_outputs=[{"tool_call_id": "0", "output": expected_out}],
                event_handler=None,
            )
            submit_tool_mock.reset_mock()
        else:
            submit_tool_mock.assert_not_called()

    @patch("azure.ai.agents._client.PipelineClient")
    @pytest.mark.skip("Recordings not yet available")
    @pytest.mark.parametrize(
        "file_agent_1,add_azure_fn",
        [
            ("file_for_agent1", True),
            (None, True),
            ("file_for_agent1", False),
            (None, False),
        ],
    )
    def test_handle_submit_tool_outputs(
        self,
        mock_pipeline_client_gen: MagicMock,
        file_agent_1: Optional[str],
        add_azure_fn: bool,
    ) -> None:
        """Test handling of stream tools response."""
        toolset = self.get_toolset(file_agent_1, function1)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            self._get_agent_json("first", "123", toolset),
            self._get_run("run123", toolset, add_azure_fn=add_azure_fn),  # create_run
            self._get_run("run123", toolset, add_azure_fn=add_azure_fn),  # get_run
            self._get_run(
                "run123", toolset, add_azure_fn=add_azure_fn, is_complete=True
            ),  # get_run after resubmitting with tool results
        ]
        mock_pipeline_response = MagicMock()
        mock_pipeline_response.http_response = mock_response
        mock_pipeline = MagicMock()
        mock_pipeline._pipeline.run.return_value = mock_pipeline_response
        mock_pipeline_client_gen.return_value = mock_pipeline
        agents_client = self.get_mock_client()
        with agents_client:
            # Check that pipelines are created as expected.
            self._set_toolcalls(agents_client, toolset, None)
            agent1 = agents_client.create_agent(
                model="gpt-4-1106-preview",
                name="first",
                instructions="You are a helpful agent",
                toolset=toolset,
            )
            # Create run with new tool set, which also can be none.
            run = agents_client.runs.create_and_process(
                thread_id="some_thread_id", agent_id=agent1.id, polling_interval=0
            )
            self._assert_tool_call(agents_client.submit_tool_outputs_to_run, "run123", toolset)
            agents_client._handle_submit_tool_outputs(run)
            self._assert_stream_call(agents_client.submit_tool_outputs_to_stream, "run123", toolset)


class TestIntegrationAgentsMock:

    def submit_tool_outputs(
        self, thread_id: str, run_id: str, *, tool_outputs: List[ToolOutput], stream_parameter: bool, stream: bool
    ) -> Iterator[bytes]:
        assert thread_id == "thread_01"
        assert run_id == "run_01"
        assert stream_parameter == True
        assert stream == True
        if (
            len(tool_outputs) == 2
            and tool_outputs[0]["tool_call_id"] == "call_01"
            and tool_outputs[1]["tool_call_id"] == "call_02"
        ):
            return convert_to_byte_iterator(fetch_current_datetime_and_weather_stream_response)
        elif len(tool_outputs) == 1 and tool_outputs[0]["tool_call_id"] == "call_03":
            return convert_to_byte_iterator(send_email_stream_response)
        raise ValueError("Unexpected tool outputs")

    @patch(
        "azure.ai.agents.operations._operations.RunsOperations.create",
        return_value=convert_to_byte_iterator(main_stream_response),
    )
    @patch("azure.ai.agents.AgentsClient.__init__", return_value=None)
    @patch(
        "azure.ai.agents.operations._operations.RunsOperations.submit_tool_outputs",
    )
    def test_create_stream_with_tool_calls(self, mock_submit_tool_outputs_to_run: Mock, *args):
        mock_submit_tool_outputs_to_run.side_effect = self.submit_tool_outputs
        functions = FunctionTool(user_functions)
        toolset = ToolSet()
        toolset.add(functions)

        operation = AgentsClient(
            endpoint="www.bcac95dd-a1eb-11ef-978f-8c1645fec84b.com",
            credential=MagicMock(),
        )
        operation.runs = RunsOperations(MagicMock(), MagicMock(), MagicMock(), MagicMock())
        operation.enable_auto_function_calls(toolset)
        count = 0

        with operation.runs.stream(thread_id="thread_id", agent_id="asst_01") as stream:
            for _ in stream:
                count += 1
        assert count == (
            main_stream_response.count("event:")
            + fetch_current_datetime_and_weather_stream_response.count("event:")
            + send_email_stream_response.count("event:")
        )
