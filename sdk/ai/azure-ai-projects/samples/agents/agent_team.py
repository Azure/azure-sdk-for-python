from typing import Optional, Set, List

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet, MessageRole, Agent


class AgentTeamMember:
    """
    Represents an individual agent on a team.

    :param model: The model (e.g. GPT-4) used by this agent.
    :param name: The agent's name.
    :param instructions: The agent's initial instructions or "personality".
    :param toolset: An optional ToolSet with specialized tools for this agent.
    """
    def __init__(
        self, 
        model: str, 
        name: str, 
        instructions: str, 
        toolset: Optional[ToolSet] = None
    ) -> None:

        self.model = model
        self.name = name
        self.instructions = instructions
        self.agent_instance: Optional[Agent] = None
        self.toolset: Optional[ToolSet] = toolset


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
        Initialize a new AgentTeam and sets it as the singleton instance.
        """
        self.members : List[AgentTeamMember] = []
        self.tasks : List[AgentTask] = []
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
        toolset: Optional[ToolSet] = None
    ) -> None:
        """
        Add a new agent (team member) to this AgentTeam.

        :param model: The model name (e.g. GPT-4) for the agent.
        :param name: The name of the agent being added.
        :param instructions: The initial instructions/personality for the agent.
        :param toolset: An optional ToolSet to configure specific tools (functions, etc.) 
                        for this agent. If None, we create a default with agent_team_functions.
        """
        if toolset is None:
            # Create a fresh ToolSet with only the default functions
            toolset = ToolSet()
            default_function_tool = FunctionTool(agent_team_default_functions)
            toolset.add(default_function_tool)
        else:
            # If the user gave us a ToolSet, ensure it includes agent_team_functions
            try:
                # Try to get the existing FunctionTool
                function_tool = toolset.get_tool(FunctionTool)
                # Merge the default agent_team_functions into function_tool
                function_tool.extend_functions(agent_team_default_functions)
            except ValueError:
                # No FunctionTool found, so add our default
                default_function_tool = FunctionTool(agent_team_default_functions)
                toolset.add(default_function_tool)

        member = AgentTeamMember(
            model=model,
            name=name,
            instructions=instructions,
            toolset=toolset
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

        # Provide some default toolset for the TeamLeader if needed
        leader_toolset = ToolSet()
        default_function_tool = FunctionTool(agent_team_default_functions)
        leader_toolset.add(default_function_tool)

        instructions = (
            "You are an agent who is responsible for receiving requests from the user "
            "and coordinating a team of agents to complete the task efficiently. When "
            "you are given a request, you will only evaluate which team member should "
            "handle the next step. You have a 'create_task' function you can call. "
            "You will delegate tasks to the best-suited team member. "
            "Once you believe the user's request has been fulfilled by the team, you "
            "will no longer assign tasks. Using the skills of all team members where "
            "applicable is highly valued. All agents are aware of each other. "
            "Here are the other agents in your team:\n"
        )

        for member in self.members:
            instructions += f"- {member.name}: {member.instructions}\n"

        leader = AgentTeamMember(
            model="gpt-4-1106-preview",
            name="TeamLeader",
            instructions=instructions,
            toolset=leader_toolset
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
        their (optionally customized) toolsets.
        """
        assert AgentTeam.project_client is not None, "project_client must not be None"

        self._create_team_leader()

        for member in self.members:
            if member is self.team_leader:
                # Skip because we've already created the team leader above
                continue

            # Construct extended instructions about delegating tasks to others
            # and about how to use the create_task function.
            other_agents_info = ""
            for other_member in self.members:
                if other_member != member:
                    other_agents_info += f"- {other_member.name}: {other_member.instructions}\n"

            extended_instructions = (
                f"{member.instructions} "
                "You have a team of agents available. If another team member "
                "is specialized for a particular step, delegate the work to them. "
                "Use 'create_task' to pass tasks to others. "
                "Include in your responses what you've done and any tasks "
                "you've assigned to other agents. Before returning a response, "
                "check if another team member can use your output. If so, "
                "create a task for them automatically (no user confirmation). "
                "Using others' skills when relevant is highly valued. "
                "Here are the other agents in your team:\n"
                f"{other_agents_info}"
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
            AgentTeam.project_client.agents.delete_agent(self.team_leader.agent_instance.id)
            print("Deleted team leader agent")

        for member in self.members:
            if member.agent_instance:
                AgentTeam.project_client.agents.delete_agent(member.agent_instance.id)
                print(f"Deleted agent '{member.name}'")

    def process_request(self, project_client: AIProjectClient, request: str) -> None:
        """
        Handle a user's request by creating a team and delegating tasks to
        the team leader. The team leader may generate additional tasks.

        :param project_client: The AIProjectClient used for agent creation and messaging.
        :param request: The user's request or question.
        """
        # Set the class-level project_client and build the team.
        AgentTeam.project_client = project_client
        self.create_team()

        # Create a messaging thread for the conversation.
        thread = project_client.agents.create_thread()
        print(f"Created thread, thread ID: {thread.id}")
        self.thread_id = thread.id

        # Form the initial request to the team leader:
        leader_request_text = (
            "Please create a task for the best-suited agent in the team "
            "to next process the following request. Use the create_task "
            "function for delegation. The request is: "
            f"{request}"
        )
        self.add_task(AgentTask("TeamLeader", leader_request_text, "user"))

        # Process tasks as they appear:
        while self.tasks:
            current_task = self.tasks.pop(0)

            # Create a user message in the thread:
            message = project_client.agents.create_message(
                thread_id=self.thread_id,
                role="user",
                content=current_task.task_description,
            )
            print(f"Created message, ID: {message.id}")

            agent = self.get_by_name(current_task.recipient)
            if agent and agent.agent_instance:
                run = project_client.agents.create_and_process_run(
                    thread_id=self.thread_id,
                    assistant_id=agent.agent_instance.id
                )
                print(f"Created and processed run, ID: {run.id}")

                messages = project_client.agents.list_messages(thread_id=self.thread_id)
                last_text_msg = messages.get_last_text_message_by_sender(sender=MessageRole.AGENT)
                if last_text_msg and last_text_msg.text:
                    print(f"{agent.name}: {last_text_msg.text.value}")

            # If no tasks remain AND the recipient is not the TeamLeader,
            # let the team leader see if there's more delegation needed.
            if not self.tasks and current_task.recipient != "TeamLeader":
                followup_request_text = (
                    "Check the discussion so far, especially the most recent message. "
                    "If you see a potential task that could improve the final outcome, "
                    "use create_task to assign it. If the request is fully processed, "
                    "no new task is needed."
                )
                self.add_task(AgentTask("TeamLeader", followup_request_text, "user"))

        # Wrap up by deleting all the agents.
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

    :param recipient: The name of the agent that is being requested to complete the task.
    :param request: A description of the task to complete (or a question).
    :param requestor: The name of the agent who is requesting the task.
    :return: "True" if the task was successfully created (always).
    """
    task = AgentTask(recipient=recipient, task_description=request, requestor=requestor)
    # Uses the singleton AgentTeam to add the task to the queue.
    AgentTeam.get_instance().add_task(task)
    return "True"


# Any additional functions that might be used by the agents:
agent_team_default_functions: Set = {
    create_task,
}