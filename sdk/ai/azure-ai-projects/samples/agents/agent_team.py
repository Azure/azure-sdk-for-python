from typing import Optional, Set, List

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet, MessageRole, Agent


TEAM_LEADER_INSTRUCTIONS = """\
You are an agent named 'TeamLeader'. Your primary role is to coordinate the work among all agents and ensure the user's requests are fulfilled by utilizing each team member's specialized skills. 
Actively look for opportunities to leverage the unique strengths of all agents. When you determine that another agent’s expertise or perspective can add value, use the create_task function to delegate, always passing 'TeamLeader' as the 'requestor'. 
Continue delegating tasks only as long as they are necessary to achieve the best possible outcome, and once you believe the user's request has been fully addressed, do not create any additional tasks. 
It is essential that you harness the collective abilities of the team—this is highly valued and reflects your effectiveness as a coordinator.
Below are your team members:
"""

TEAM_MEMBER_CAN_DELEGATE_INSTRUCTIONS = """\
You are an agent named '{name}'. 
{original_instructions}

• You can delegate tasks when appropriate. To delegate, call the create_task function, using your own name as the 'requestor'. 
• Provide a brief account of any tasks you assign and the outcome. 
• Ask for help from other team members if you see they have the relevant expertise. 
• Once you believe your assignment is complete, respond with your final answer or actions taken. 
• Below are the other agents in your team:
{other_agents_info}
"""

TEAM_MEMBER_NO_DELEGATE_INSTRUCTIONS = """\
You are an agent named '{name}'. 
{original_instructions}

• You do not delegate tasks. Instead, focus solely on fulfilling the tasks assigned to you. 
• If you have suggestions for tasks better suited to another agent, simply mention it in your response, but do not call create_task yourself. 
• Once you believe your assignment is complete, respond with your final answer or actions taken. 
• Below are the other agents in your team:
{other_agents_info}
"""


class AgentTeamMember:
    """
    Represents an individual agent on a team.

    :param model: The model (e.g. GPT-4) used by this agent.
    :param name: The agent's name.
    :param instructions: The agent's initial instructions or "personality".
    :param toolset: An optional ToolSet with specialized tools for this agent.
    :param can_delegate: Whether this agent has delegation capability (e.g., 'create_task').
                         Defaults to True.
    """
    def __init__(
        self,
        model: str,
        name: str,
        instructions: str,
        toolset: Optional[ToolSet] = None,
        can_delegate: bool = True
    ) -> None:
        self.model = model
        self.name = name
        self.instructions = instructions
        self.agent_instance: Optional[Agent] = None
        self.toolset: Optional[ToolSet] = toolset
        self.can_delegate = can_delegate


class AgentTask:
    """
    Encapsulates a task for an agent to perform.

    :param recipient: The name of the agent who should receive the task.
    :param task_description: The description of the work to be done or question to be answered.
    :param requestor: The name of the agent or user requesting the task.
    """
    def __init__(self, recipient: str, task_description: str, requestor: str) -> None:
        self.recipient = recipient
        self.task_description = task_description
        self.requestor = requestor


class AgentTeam:
    """
    Manages a team of agents and their tasks.
    """

    project_client: Optional[AIProjectClient] = None
    instance: Optional["AgentTeam"] = None

    def __init__(self) -> None:
        """
        Initialize a new AgentTeam and set it as the singleton instance.
        """
        self.members: List[AgentTeamMember] = []
        self.tasks: List[AgentTask] = []
        self.team_leader: Optional[AgentTeamMember] = None
        self.thread_id: str = ""
        AgentTeam.instance = self

    @classmethod
    def get_instance(cls) -> "AgentTeam":
        """
        Retrieve the current singleton AgentTeam instance.
        Raises ValueError if no instance has been created yet.
        """
        if cls.instance is None:
            raise ValueError("No AgentTeam instance has been created.")
        return cls.instance

    def add_agent(
        self,
        model: str,
        name: str,
        instructions: str,
        toolset: Optional[ToolSet] = None,
        can_delegate: bool = True
    ) -> None:
        """
        Add a new agent (team member) to this AgentTeam.

        :param model: The model name (e.g. GPT-4) for the agent.
        :param name: The name of the agent being added.
        :param instructions: The initial instructions/personality for the agent.
        :param toolset: An optional ToolSet to configure specific tools (functions, etc.)
                        for this agent. If None, we'll create a default set.
        :param can_delegate: If True, the agent can delegate tasks (via create_task).
                            If False, the agent does not get 'create_task' in its ToolSet
                            and won't mention delegation in instructions.
        """
        if toolset is None:
            toolset = ToolSet()

        if can_delegate:
            # If agent can delegate, ensure it has 'create_task'
            try:
                function_tool = toolset.get_tool(FunctionTool)
                function_tool.extend_functions(agent_team_default_functions)
            except ValueError:
                default_function_tool = FunctionTool(agent_team_default_functions)
                toolset.add(default_function_tool)

        member = AgentTeamMember(
            model=model,
            name=name,
            instructions=instructions,
            toolset=toolset,
            can_delegate=can_delegate,
        )
        self.members.append(member)

    def add_task(self, task: AgentTask) -> None:
        """
        Add a new task to the team's task list.

        :param task: The task to be added.
        """
        self.tasks.append(task)

    def _create_team_leader(self) -> None:
        """
        Create and initialize the 'TeamLeader' agent with awareness of all other agents.
        """
        assert AgentTeam.project_client is not None, "project_client must not be None"

        leader_toolset = ToolSet()
        default_function_tool = FunctionTool(agent_team_default_functions)
        leader_toolset.add(default_function_tool)

        instructions = TEAM_LEADER_INSTRUCTIONS + "\n"
        # List all agents (will be empty at this moment if you haven’t added any, or you can append after they’re added)
        for member in self.members:
            if member.name != "TeamLeader":
                instructions += f"- {member.name}: {member.instructions}\n"

        leader = AgentTeamMember(
            model="gpt-4-1106-preview",
            name="TeamLeader",
            instructions=instructions,
            toolset=leader_toolset,
            can_delegate=True,
        )
        leader.agent_instance = AgentTeam.project_client.agents.create_agent(
            model=leader.model,
            name=leader.name,
            instructions=leader.instructions,
            toolset=leader.toolset,
        )

        self.team_leader = leader

    def create_team(self) -> None:
        """
        Create the team leader agent and initialize all member agents with
        their configured or default toolsets.
        """
        assert AgentTeam.project_client is not None, "project_client must not be None"

        self._create_team_leader()

        for member in self.members:
            if member is self.team_leader:
                continue

            # Build a list of other agents (besides the current one).
            other_agents_info = ""
            for other_member in self.members:
                if other_member != member:
                    other_agents_info += f"- {other_member.name}: {other_member.instructions}\n"

            if member.can_delegate:
                extended_instructions = TEAM_MEMBER_CAN_DELEGATE_INSTRUCTIONS.format(
                    name=member.name,
                    original_instructions=member.instructions,
                    other_agents_info=other_agents_info
                )
            else:
                extended_instructions = TEAM_MEMBER_NO_DELEGATE_INSTRUCTIONS.format(
                    name=member.name,
                    original_instructions=member.instructions,
                    other_agents_info=""
                )

            member.agent_instance = AgentTeam.project_client.agents.create_agent(
                model=member.model,
                name=member.name,
                instructions=extended_instructions,
                toolset=member.toolset,
            )

    def dismantle_team(self) -> None:
        """
        Delete all agents (including the team leader) from the project client.
        """
        assert AgentTeam.project_client is not None, "project_client must not be None"

        if self.team_leader and self.team_leader.agent_instance:
            print(f"Deleting team leader agent '{self.team_leader.name}'")
            AgentTeam.project_client.agents.delete_agent(self.team_leader.agent_instance.id)

        for member in self.members:
            if member is not self.team_leader and member.agent_instance:
                print(f"Deleting agent '{member.name}'")
                AgentTeam.project_client.agents.delete_agent(member.agent_instance.id)

    def process_request(self, project_client: AIProjectClient, request: str) -> None:
        """
        Handle a user's request by creating a team and delegating tasks to
        the team leader. The team leader may generate additional tasks.

        :param project_client: The AIProjectClient used for agent creation and messaging.
        :param request: The user's request or question.
        """
        AgentTeam.project_client = project_client
        self.create_team()

        thread = project_client.agents.create_thread()
        print(f"Created thread with ID: {thread.id}")
        self.thread_id = thread.id

        leader_request_text = (
            "Please create a task for the best-suited agent in the team "
            "to next process the following request. Use the create_task "
            "function for delegation. The request is: "
            f"{request}"
        )
        self.add_task(AgentTask("TeamLeader", leader_request_text, "user"))

        while self.tasks:
            current_task = self.tasks.pop(0)

            print(
                f"Starting task for agent '{current_task.recipient}'. "
                f"Requestor: '{current_task.requestor}'. "
                f"Task description: '{current_task.task_description}'."
            )

            message = project_client.agents.create_message(
                thread_id=self.thread_id,
                role="user",
                content=current_task.task_description,
            )
            print(f"Created message with ID: {message.id} for task in thread {self.thread_id}")

            agent = self.get_by_name(current_task.recipient)
            if agent and agent.agent_instance:
                run = project_client.agents.create_and_process_run(
                    thread_id=self.thread_id,
                    assistant_id=agent.agent_instance.id
                )
                print(f"Created and processed run for agent '{agent.name}', run ID: {run.id}")

                messages = project_client.agents.list_messages(thread_id=self.thread_id)
                last_text_msg = messages.get_last_text_message_by_sender(sender=MessageRole.AGENT)
                if last_text_msg and last_text_msg.text:
                    print(
                        f"Agent '{agent.name}' completed task. "
                        f"Outcome: {last_text_msg.text.value}"
                    )

            # If no tasks remain AND the recipient is not the TeamLeader,
            # let the TeamLeader see if more delegation is needed.
            if not self.tasks and current_task.recipient != "TeamLeader":
                followup_request_text = (
                    "Check the discussion so far, especially the most recent message. "
                    "If you see a potential task that could improve the final outcome, "
                    "use create_task to assign it. If the request is fully processed, "
                    "no new task is needed and finally summarize the outcome."
                )
                self.add_task(AgentTask("TeamLeader", followup_request_text, "user"))

        self.dismantle_team()

    def get_by_name(self, name: str) -> Optional[AgentTeamMember]:
        """
        Retrieve a team member (agent) by name.
        If no member with the specified name is found, returns None.

        :param name: The agent's name within this team.
        """
        if name == "TeamLeader":
            return self.team_leader
        for member in self.members:
            if member.name == name:
                return member
        return None


def create_task(recipient: str, request: str, requestor: str) -> str:
    """
    Requests another agent in the team to complete a task.

    :param recipient: Name of the agent that is being requested to complete the task.
    :param request: A description of the task to complete (or a question).
    :param requestor: The name of the agent who is requesting the task.
    :return: "True" if the task was successfully created (always).
    """
    task = AgentTask(recipient=recipient, task_description=request, requestor=requestor)
    AgentTeam.get_instance().add_task(task)
    return "True"


# Any additional functions that might be used by the agents:
agent_team_default_functions: Set = {
    create_task,
}