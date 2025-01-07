# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Dict, List, Optional
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet, MessageRole, Agent


class _AgentTeamMember:
    agent_instance: Optional[Agent]

    def __init__(self, model, name, instructions):
        self.model = model
        self.name = name
        self.instructions = instructions
        self.agent_instance = None


class _AgentTask:
    def __init__(self, recipient: str, task_description: str, requestor: str):
        self.recipient = recipient
        self.task_description = task_description
        self.requestor = requestor


class AgentTeam:
    """
    A class that represents a team of agents.

    """

    # Static container to store all instances of AgentTeam
    _teams: Dict[str, "AgentTeam"] = {}

    _project_client: AIProjectClient
    _thread_id: str = ""
    _team_leader: Optional[_AgentTeamMember] = None
    _members: List[_AgentTeamMember] = []
    _tasks: List[_AgentTask] = []

    def __init__(self, team_name: str, project_client: AIProjectClient):
        # Validate that the team_name is a non-empty string
        if not isinstance(team_name, str) or not team_name:
            raise ValueError("Team name must be a non-empty string.")
        # Check for existing team with the same name
        if team_name in AgentTeam._teams:
            raise ValueError(f"A team with the name '{team_name}' already exists.")
        self.team_name = team_name
        if project_client is None:
            raise ValueError("No AIProjectClient provided.")
        self._project_client = project_client
        # Store the instance in the static container
        AgentTeam._teams[team_name] = self

    @staticmethod
    def get_team(team_name: str) -> "AgentTeam":
        """Static method to fetch the AgentTeam instance by name."""
        team = AgentTeam._teams.get(team_name)
        if team is None:
            raise ValueError(f"No team found with the name '{team_name}'.")
        return team

    @staticmethod
    def _remove_team(team_name: str) -> None:
        """Static method to remove an AgentTeam instance by name."""
        if team_name not in AgentTeam._teams:
            raise ValueError(f"No team found with the name '{team_name}'.")
        del AgentTeam._teams[team_name]

    def add_agent(self, model, name, instructions):
        member = _AgentTeamMember(model, name, instructions)
        self._members.append(member)

    def _add_task(self, task: _AgentTask):
        self._tasks.append(task)

    def _create_team_leader(self):
        toolset = ToolSet()
        toolset.add(functions)
        instructions = f"You are a leader of a team of agents. The name of your team is {self.team_name}"
        "You are an agent that is responsible for receiving requests from user and utilizing a team of agents to complete the task. "
        "When you are passed a request, the only thing you will do is evaluate which team member should do which task next to complete the request. "
        "You will use the provided create_task function to create a task for the agent that is "
        "best suited for handling the task next. You will respond with the description of who you assigned the task and why. "
        "When you think that the original user request is processed completely utilizing all the talent available in the team, "
        "you do not have to create anymore tasks. Using the skills of all the team members when applicable is highly valued. "
        "All of the agents in the team are aware of each other and can also create tasks for each other. "
        "Here are the other agents in your team:\n"

        for member in self._members:
            instructions += f"- {member.name}: {member.instructions}\n"

        self._team_leader = _AgentTeamMember(model="gpt-4-1106-preview", name="TeamLeader", instructions=instructions)
        if self._project_client is not None:
            self._team_leader.agent_instance = self._project_client.agents.create_agent(
                model="gpt-4-1106-preview", name="TeamLeader", instructions=instructions, toolset=toolset
            )

    def assemble_team(self):
        self._create_team_leader()
        # Initialize function tool with agent team functions
        toolset = ToolSet()
        toolset.add(functions)
        for member in self._members:
            extended_instructions = (
                f"{member.instructions} You are a member in a team of agents. The name of your team is {self.team_name}"
                f"If there is a member in the team that is specialized in a certain task, you must utilize their help to complete the task. "
                f"When you want to pass the task to another agent, use the create_task function passing in the agent name to whom you want to "
                f"assign the task and your task description as parameters. The third parameter to the function will be your name. "
                f"After assigning the task, you can respond with description of what you did as part of your work and also include "
                f"information about any tasks you assigned to other agents. As part of any request, before returning any response, you must consider if there is "
                f"another team member that can use your output as their input. If there is such team member, you have to create a task for them "
                f"using the provided function. You must not ask the user to confirm the task creation, you will just do it. "
                f"Use the actual function call tool, do not just write it as python code. "
                f"Using the skills of other team members when applicable is highly valued. "
                f"Here are the other agents in your team:\n"
            )
            for other_member in self._members:
                if other_member != member:
                    extended_instructions += f"- {other_member.name}: {other_member.instructions}\n"

            if self._project_client is not None:
                member.agent_instance = self._project_client.agents.create_agent(
                    model=member.model, name=member.name, instructions=extended_instructions, toolset=toolset
                )
        thread = self._project_client.agents.create_thread()
        print(f"Created thread, thread ID: {thread.id}")
        self._thread_id = thread.id

    def dismantle_team(self):
        if self._project_client is not None:
            if self._team_leader is not None:
                if self._team_leader.agent_instance is not None:
                    self._project_client.agents.delete_agent(self._team_leader.agent_instance.id)
                    print("Deleted agent")
        for member in self._members:
            if self._project_client is not None:
                if member.agent_instance is not None:
                    self._project_client.agents.delete_agent(member.agent_instance.id)
                    print("Deleted agent")
        AgentTeam._remove_team(self.team_name)

    def process_request(self, request: str):
        team_leader_request = (
            "Please create a task for agent in the team that is best suited to next process the following request. Use the create_task function available for you to create the task. The request is: "
            + request
        )
        task = _AgentTask(recipient="TeamLeader", task_description=team_leader_request, requestor="user")
        self._add_task(task)
        while self._tasks:
            task = self._tasks.pop(0)
            message = self._project_client.agents.create_message(
                thread_id=self._thread_id,
                role="user",
                content=task.task_description,
            )
            print(f"Created message, ID: {message.id}")
            agent = self._get_member_by_name(task.recipient)
            if agent is not None:
                if agent.agent_instance is not None:
                    run = self._project_client.agents.create_and_process_run(
                        thread_id=self._thread_id, assistant_id=agent.agent_instance.id
                    )
                    print(f"Created and processed run, ID: {run.id}")
            messages = self._project_client.agents.get_messages(thread_id=self._thread_id)
            text_message = messages.get_last_text_message_by_role(role=MessageRole.AGENT)
            if text_message is not None:
                message_content = text_message.text.value
                if agent is not None:
                    print(f"{agent.name}: {message_content}")
            if not self._tasks and not task.recipient == "TeamLeader":
                team_leader_request = (
                    "Check the discussion so far and especially the most recent message in the thread. "
                )
                "If you can think of a task that would help achieve more high quality end result, then use the create_task function to create the task. "
                "Do not ever ask user confirmation for creating a task. "
                "If the request is completely processed, you do not have to create a task."
                task = _AgentTask(recipient="TeamLeader", task_description=team_leader_request, requestor="user")
                self._add_task(task)

    def _get_member_by_name(self, name) -> Optional[_AgentTeamMember]:
        if name == "TeamLeader":
            return self._team_leader
        for member in self._members:
            if member.name == name:
                return member
        return None


def _create_task(team_name: str, recipient: str, request: str, requestor: str) -> str:
    """
    Requests another agent in the team to complete a task.

    :param team_name (str): The name of the team.
    :param recipient (str): The name of the agent that is being requested to complete the task.
    :param request (str): A description of the to complete. This can also be a question.
    :param requestor (str): The name of the agent who is requesting the task.
    :return: True if the task was successfully received, False otherwise.
    :rtype: str
    """
    task = _AgentTask(recipient=recipient, task_description=request, requestor=requestor)
    team: Optional[AgentTeam] = None
    try:
        team = AgentTeam.get_team(team_name)
    except:
        pass
    if team is not None:
        team._add_task(task)
        return "True"
    return "False"


# Statically defined agent team functions for fast reference
agent_team_functions = {
    _create_task,
}

functions = FunctionTool(functions=agent_team_functions)
