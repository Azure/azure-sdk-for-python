# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import yaml  # type: ignore

from opentelemetry import trace
from opentelemetry.trace import StatusCode, Span  # noqa: F401 # pylint: disable=unused-import
from typing import Any, Dict, Optional, Set, List
from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.models import FunctionTool, ToolSet, MessageRole, Assistant, AssistantThread

tracer = trace.get_tracer(__name__)


class _AssistantTeamMember:
    """
    Represents an individual assistant on a team.

    :param model: The model (e.g. GPT-4) used by this assistant.
    :param name: The assistant's name.
    :param instructions: The assistant's initial instructions or "personality".
    :param toolset: An optional ToolSet with specialized tools for this assistant.
    :param can_delegate: Whether this assistant has delegation capability (e.g., 'create_task').
                         Defaults to True.
    """

    def __init__(
        self, model: str, name: str, instructions: str, toolset: Optional[ToolSet] = None, can_delegate: bool = True
    ) -> None:
        self.model = model
        self.name = name
        self.instructions = instructions
        self.assistant_instance: Optional[Assistant] = None
        self.toolset: Optional[ToolSet] = toolset
        self.can_delegate = can_delegate


class AssistantTask:
    """
    Encapsulates a task for an assistant to perform.

    :param recipient: The name of the assistant who should receive the task.
    :param task_description: The description of the work to be done or question to be answered.
    :param requestor: The name of the assistant or user requesting the task.
    """

    def __init__(self, recipient: str, task_description: str, requestor: str) -> None:
        self.recipient = recipient
        self.task_description = task_description
        self.requestor = requestor


class AssistantTeam:
    """
    A class that represents a team of assistants.

    """

    # Static container to store all instances of AssistantTeam
    _teams: Dict[str, "AssistantTeam"] = {}

    _assistants_client: AssistantsClient
    _assistant_thread: Optional[AssistantThread] = None
    _team_leader: Optional[_AssistantTeamMember] = None
    _members: List[_AssistantTeamMember] = []
    _tasks: List[AssistantTask] = []
    _team_name: str = ""
    _current_request_span: Optional[Span] = None
    _current_task_span: Optional[Span] = None

    def __init__(self, team_name: str, assistants_client: AssistantsClient):
        """
        Initialize a new AssistantTeam and set it as the singleton instance.
        """
        # Validate that the team_name is a non-empty string
        if not isinstance(team_name, str) or not team_name:
            raise ValueError("Team name must be a non-empty string.")
        # Check for existing team with the same name
        if team_name in AssistantTeam._teams:
            raise ValueError(f"A team with the name '{team_name}' already exists.")
        self.team_name = team_name
        if assistants_client is None:
            raise ValueError("No AssistantsClient provided.")
        self._assistants_client = assistants_client
        # Store the instance in the static container
        AssistantTeam._teams[team_name] = self

        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the full path to the config file
        file_path = os.path.join(current_dir, "assistant_team_config.yaml")
        with open(file_path, "r") as config_file:
            config = yaml.safe_load(config_file)
            self.TEAM_LEADER_INSTRUCTIONS = config["TEAM_LEADER_INSTRUCTIONS"]
            self.TEAM_LEADER_INITIAL_REQUEST = config["TEAM_LEADER_INITIAL_REQUEST"]
            self.TEAM_LEADER_TASK_COMPLETENESS_CHECK_INSTRUCTIONS = config[
                "TEAM_LEADER_TASK_COMPLETENESS_CHECK_INSTRUCTIONS"
            ]
            self.TEAM_MEMBER_CAN_DELEGATE_INSTRUCTIONS = config["TEAM_MEMBER_CAN_DELEGATE_INSTRUCTIONS"]
            self.TEAM_MEMBER_NO_DELEGATE_INSTRUCTIONS = config["TEAM_MEMBER_NO_DELEGATE_INSTRUCTIONS"]
            self.TEAM_LEADER_MODEL = config["TEAM_LEADER_MODEL"].strip()

    @staticmethod
    def get_team(team_name: str) -> "AssistantTeam":
        """Static method to fetch the AssistantTeam instance by name."""
        team = AssistantTeam._teams.get(team_name)
        if team is None:
            raise ValueError(f"No team found with the name '{team_name}'.")
        return team

    @staticmethod
    def _remove_team(team_name: str) -> None:
        """Static method to remove an AssistantTeam instance by name."""
        if team_name not in AssistantTeam._teams:
            raise ValueError(f"No team found with the name '{team_name}'.")
        del AssistantTeam._teams[team_name]

    def add_assistant(
        self, model: str, name: str, instructions: str, toolset: Optional[ToolSet] = None, can_delegate: bool = True
    ) -> None:
        """
        Add a new assistant (team member) to this AssistantTeam.

        :param model: The model name (e.g. GPT-4) for the assistant.
        :param name: The name of the assistant being added.
        :param instructions: The initial instructions/personality for the assistant.
        :param toolset: An optional ToolSet to configure specific tools (functions, etc.)
                        for this assistant. If None, we'll create a default set.
        :param can_delegate: If True, the assistant can delegate tasks (via create_task).
                            If False, the assistant does not get 'create_task' in its ToolSet
                            and won't mention delegation in instructions.
        """
        if toolset is None:
            toolset = ToolSet()

        if can_delegate:
            # If assistant can delegate, ensure it has 'create_task'
            try:
                function_tool = toolset.get_tool(FunctionTool)
                function_tool.add_functions(assistant_team_default_functions)
            except ValueError:
                default_function_tool = FunctionTool(assistant_team_default_functions)
                toolset.add(default_function_tool)

        member = _AssistantTeamMember(
            model=model,
            name=name,
            instructions=instructions,
            toolset=toolset,
            can_delegate=can_delegate,
        )
        self._members.append(member)

    def set_team_leader(self, model: str, name: str, instructions: str, toolset: Optional[ToolSet] = None) -> None:
        """
        Set the team leader for this AssistantTeam.

        If team leader has not been set prior to the call to assemble_team,
        then a default team leader will be set.

        :param model: The model name (e.g. GPT-4) for the assistant.
        :param name: The name of the team leader.
        :param instructions: The instructions for the team leader. These instructions
                             are not modified by the implementation, so all required
                             information about other team members and how to pass tasks
                             to them should be included.
        :param toolset: An optional ToolSet to configure specific tools (functions, etc.)
                        for the team leader.
        """
        member = _AssistantTeamMember(model=model, name=name, instructions=instructions, toolset=toolset)
        self._team_leader = member

    def add_task(self, task: AssistantTask) -> None:
        """
        Add a new task to the team's task list.

        :param task: The task to be added.
        """
        self._tasks.append(task)

    def _create_team_leader(self) -> None:
        """
        Create the team leader assistant.
        """
        assert self._assistants_client is not None, "assistants_client must not be None"
        assert self._team_leader is not None, "team leader has not been added"

        self._team_leader.assistant_instance = self._assistants_client.create_assistant(
            model=self._team_leader.model,
            name=self._team_leader.name,
            instructions=self._team_leader.instructions,
            toolset=self._team_leader.toolset,
        )

    def _set_default_team_leader(self):
        """
        Set the default 'TeamLeader' assistant with awareness of all other assistants.
        """
        toolset = ToolSet()
        toolset.add(default_function_tool)
        instructions = (
            self.TEAM_LEADER_INSTRUCTIONS.format(assistant_name="TeamLeader", team_name=self.team_name) + "\n"
        )
        # List all assistants (will be empty at this moment if you haven't added any, or you can append after they're added)
        for member in self._members:
            instructions += f"- {member.name}: {member.instructions}\n"

        self._team_leader = _AssistantTeamMember(
            model=self.TEAM_LEADER_MODEL,
            name="TeamLeader",
            instructions=instructions,
            toolset=toolset,
            can_delegate=True,
        )

    def assemble_team(self):
        """
        Create the team leader assistant and initialize all member assistants with
        their configured or default toolsets.
        """
        assert self._assistants_client is not None, "assistants_client must not be None"

        if self._team_leader is None:
            self._set_default_team_leader()

        self._create_team_leader()

        for member in self._members:
            if member is self._team_leader:
                continue

            team_description = ""
            for other_member in self._members:
                if other_member != member:
                    team_description += f"- {other_member.name}: {other_member.instructions}\n"

            if member.can_delegate:
                extended_instructions = self.TEAM_MEMBER_CAN_DELEGATE_INSTRUCTIONS.format(
                    name=member.name,
                    team_name=self._team_name,
                    original_instructions=member.instructions,
                    team_description=team_description,
                )
            else:
                extended_instructions = self.TEAM_MEMBER_NO_DELEGATE_INSTRUCTIONS.format(
                    name=member.name,
                    team_name=self._team_name,
                    original_instructions=member.instructions,
                    team_description=team_description,
                )
            member.assistant_instance = self._assistants_client.create_assistant(
                model=member.model, name=member.name, instructions=extended_instructions, toolset=member.toolset
            )

    def dismantle_team(self) -> None:
        """
        Delete all assistants (including the team leader) from the project client.
        """
        assert self._assistants_client is not None, "assistants_client must not be None"

        if self._team_leader and self._team_leader.assistant_instance:
            print(f"Deleting team leader assistant '{self._team_leader.name}'")
            self._assistants_client.delete_assistant(self._team_leader.assistant_instance.id)
        for member in self._members:
            if member is not self._team_leader and member.assistant_instance:
                print(f"Deleting assistant '{member.name}'")
                self._assistants_client.delete_assistant(member.assistant_instance.id)
        AssistantTeam._remove_team(self.team_name)

    def _add_task_completion_event(
        self,
        span: Span,
        result: str,
    ) -> None:

        attributes: Dict[str, Any] = {}
        attributes["assistant_team.task.result"] = result
        span.add_event(name=f"assistant_team.task_completed", attributes=attributes)

    def process_request(self, request: str) -> None:
        """
        Handle a user's request by creating a team and delegating tasks to
        the team leader. The team leader may generate additional tasks.

        :param request: The user's request or question.
        """
        assert self._assistants_client is not None, "project client must not be None"
        assert self._team_leader is not None, "team leader must not be None"

        if self._assistant_thread is None:
            self._assistant_thread = self._assistants_client.create_thread()
            print(f"Created thread with ID: {self._assistant_thread.id}")

        with tracer.start_as_current_span("assistant_team_request") as current_request_span:
            self._current_request_span = current_request_span
            if self._current_request_span is not None:
                self._current_request_span.set_attribute("assistant_team.name", self.team_name)
            team_leader_request = self.TEAM_LEADER_INITIAL_REQUEST.format(original_request=request)
            _create_task(
                team_name=self.team_name,
                recipient=self._team_leader.name,
                request=team_leader_request,
                requestor="user",
            )
            while self._tasks:
                task = self._tasks.pop(0)
                with tracer.start_as_current_span("assistant_team_task") as current_task_span:
                    self._current_task_span = current_task_span
                    if self._current_task_span is not None:
                        self._current_task_span.set_attribute("assistant_team.name", self.team_name)
                        self._current_task_span.set_attribute("assistant_team.task.recipient", task.recipient)
                        self._current_task_span.set_attribute("assistant_team.task.requestor", task.requestor)
                        self._current_task_span.set_attribute("assistant_team.task.description", task.task_description)
                    print(
                        f"Starting task for assistant '{task.recipient}'. "
                        f"Requestor: '{task.requestor}'. "
                        f"Task description: '{task.task_description}'."
                    )
                    message = self._assistants_client.create_message(
                        thread_id=self._assistant_thread.id,
                        role="user",
                        content=task.task_description,
                    )
                    print(f"Created message with ID: {message.id} for task in thread {self._assistant_thread.id}")
                    assistant = self._get_member_by_name(task.recipient)
                    if assistant and assistant.assistant_instance:
                        run = self._assistants_client.create_and_process_run(
                            thread_id=self._assistant_thread.id, assistant_id=assistant.assistant_instance.id
                        )
                        print(f"Created and processed run for assistant '{assistant.name}', run ID: {run.id}")
                        messages = self._assistants_client.list_messages(thread_id=self._assistant_thread.id)
                        text_message = messages.get_last_text_message_by_role(role=MessageRole.ASSISTANT)
                        if text_message and text_message.text:
                            print(
                                f"Assistant '{assistant.name}' completed task. " f"Outcome: {text_message.text.value}"
                            )
                            if self._current_task_span is not None:
                                self._add_task_completion_event(self._current_task_span, result=text_message.text.value)

                    # If no tasks remain AND the recipient is not the TeamLeader,
                    # let the TeamLeader see if more delegation is needed.
                    if not self._tasks and not task.recipient == "TeamLeader":
                        team_leader_request = self.TEAM_LEADER_TASK_COMPLETENESS_CHECK_INSTRUCTIONS
                        _create_task(
                            team_name=self.team_name,
                            recipient=self._team_leader.name,
                            request=team_leader_request,
                            requestor="user",
                        )
                    # self._current_task_span.end()
                    self._current_task_span = None
            # self._current_request_span.end()
            self._current_request_span = None

    def _get_member_by_name(self, name) -> Optional[_AssistantTeamMember]:
        """
        Retrieve a team member (assistant) by name.
        If no member with the specified name is found, returns None.

        :param name: The assistant's name within this team.
        """
        if name == "TeamLeader":
            return self._team_leader
        for member in self._members:
            if member.name == name:
                return member
        return None

    """
    Requests another assistant in the team to complete a task.

    :param span (Span): The event will be added to this span
    :param team_name (str): The name of the team.
    :param recipient (str): The name of the assistant that is being requested to complete the task.
    :param request (str): A description of the to complete. This can also be a question.
    :param requestor (str): The name of the assistant who is requesting the task.
    :return: True if the task was successfully received, False otherwise.
    :rtype: str
    """


def _add_create_task_event(
    span: Span,
    team_name: str,
    requestor: str,
    recipient: str,
    request: str,
) -> None:

    attributes: Dict[str, Any] = {}
    attributes["assistant_team.task.team_name"] = team_name
    attributes["assistant_team.task.requestor"] = requestor
    attributes["assistant_team.task.recipient"] = recipient
    attributes["assistant_team.task.description"] = request
    span.add_event(name=f"assistant_team.create_task", attributes=attributes)


def _create_task(team_name: str, recipient: str, request: str, requestor: str) -> str:
    """
    Requests another assistant in the team to complete a task.

    :param team_name (str): The name of the team.
    :param recipient (str): The name of the assistant that is being requested to complete the task.
    :param request (str): A description of the to complete. This can also be a question.
    :param requestor (str): The name of the assistant who is requesting the task.
    :return: True if the task was successfully received, False otherwise.
    :rtype: str
    """
    task = AssistantTask(recipient=recipient, task_description=request, requestor=requestor)
    team: Optional[AssistantTeam] = None
    try:
        team = AssistantTeam.get_team(team_name)
        span: Optional[Span] = None
        if team._current_task_span is not None:
            span = team._current_task_span
        elif team._current_request_span is not None:
            span = team._current_request_span

        if span is not None:
            _add_create_task_event(
                span=span, team_name=team_name, requestor=requestor, recipient=recipient, request=request
            )
    except:
        pass
    if team is not None:
        team.add_task(task)
        return "True"
    return "False"


# Any additional functions that might be used by the assistants:
assistant_team_default_functions: Set = {
    _create_task,
}

default_function_tool = FunctionTool(functions=assistant_team_default_functions)
