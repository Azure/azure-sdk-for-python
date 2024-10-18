# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os, time
from azure.ai.client import AzureAIClient
from azure.ai.client.models import FunctionTool, SubmitToolOutputsAction, RequiredFunctionToolCall


class AgentTeamMember:
    def __init__(self, model, name, instructions):
        self.model = model
        self.name = name
        self.instructions = instructions
        self.agent_instance = None


class AgentTask:
    def __init__(self, recipient: str, task_description: str, requestor: str):
        self.recipient = recipient
        self.task_description = task_description
        self.requestor = requestor


class AgentTeam:
    ai_client = None
    thread_id = ""
    team_leader = None
    instance = None

    def __init__(self):
        self.members = []
        self.tasks = []
        AgentTeam.instance = self

    def add_agent(self, model, name, instructions):
        member = AgentTeamMember(model, name, instructions)
        self.members.append(member)

    def add_task(self, task: AgentTask):
        self.tasks.append(task)

    def _create_team_leader(self):
        functions = FunctionTool(functions=agent_team_functions)
        instructions = "You are an agent that is responsible for receiving requests from user and utilizing a team of agents to complete the task. "
        "When you are passed a request, the only thing you will do is evaluate which team member should do which task next to complete the request. "
        "You will use the provided create_task function to create a task for the agent that is "
        "best suited for handling the task next. You will respond with the description of who you assigned the task and why. "
        "When you think that the original user request is processed completely utilizing all the talent available in the team, "
        "you do not have to create anymore tasks. Using the skills of all the team members when applicable is highly valued. "
        "All of the agents in the team are aware of each other and can also create tasks for each other. "
        "Here are the other agents in your team:\n"

        for member in self.members:
            instructions += f"- {member.name}: {member.instructions}\n"

        self.team_leader = AgentTeamMember(model="gpt-4-1106-preview", name="TeamLeader", instructions=instructions)
        self.team_leader.agent_instance = AgentTeam.ai_client.agents.create_agent(model="gpt-4-1106-preview", name="TeamLeader", instructions=instructions, tools=functions.definitions)

    def create_team(self):
        self._create_team_leader()
        # Initialize function tool with agent team functions
        functions = FunctionTool(functions=agent_team_functions)
        for member in self.members:
            extended_instructions = (
                f"{member.instructions} You have a team of agents available to complete your task. "
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
            for other_member in self.members:
                if other_member != member:
                    extended_instructions += f"- {other_member.name}: {other_member.instructions}\n"
            member.agent_instance = AgentTeam.ai_client.agents.create_agent(model=member.model, name=member.name, instructions=extended_instructions, tools=functions.definitions)

    def dismantle_team(self):
        AgentTeam.ai_client.agents.delete_agent(self.team_leader.agent_instance.id)
        print("Deleted agent")
        for member in self.members:
            AgentTeam.ai_client.agents.delete_agent(member.agent_instance.id)
            print("Deleted agent")

    def process_request(self, ai_client: AzureAIClient, request: str):
        AgentTeam.ai_client = ai_client
        self.create_team()
        thread = ai_client.agents.create_thread()
        print(f"Created thread, thread ID: {thread.id}")
        self.thread_id = thread.id
        team_leader_request = "Please create a task for agent in the team that is best suited to next process the following request. Use the create_task function available for you to create the task. The request is: " + request
        task = AgentTask(recipient="TeamLeader", task_description=team_leader_request, requestor="user")
        self.add_task(task)
        while self.tasks:
            task = self.tasks.pop(0)
            message = ai_client.agents.create_message(
                thread_id=self.thread_id,
                role="user",
                content=task.task_description,
            )
            print(f"Created message, ID: {message.id}")
            agent = self.get_by_name(task.recipient)
            run = ai_client.agents.create_run(thread_id=self.thread_id, assistant_id=agent.agent_instance.id)
            print(f"Created run, ID: {run.id}")

            while run.status in ["queued", "in_progress", "requires_action"]:
                time.sleep(1)
                run = ai_client.agents.get_run(thread_id=self.thread_id, run_id=run.id)

                if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    if not tool_calls:
                        print("No tool calls provided - cancelling run")
                        ai_client.agents.cancel_run(thread_id=self.thread_id, run_id=run.id)
                        break

                    tool_outputs = []
                    for tool_call in tool_calls:
                        if isinstance(tool_call, RequiredFunctionToolCall):
                            try:
                                output = functions.execute(tool_call)
                                tool_outputs.append({
                                    "tool_call_id": tool_call.id,
                                    "output": output,
                                })
                            except Exception as e:
                                print(f"Error executing tool_call {tool_call.id}: {e}")
                    print(f"Tool outputs: {tool_outputs}")
                    if tool_outputs:
                        ai_client.agents.submit_tool_outputs_to_run(thread_id=self.thread_id, run_id=run.id, tool_outputs=tool_outputs)

            messages = ai_client.agents.list_messages(thread_id=self.thread_id)
            message = messages['data'][0]
            message_content = message['content'][0]['text']['value']
            print(f"{agent.name}: {message_content}")
            if not self.tasks and not task.recipient == "TeamLeader":
                team_leader_request = "Check the discussion so far and especially the most recent message in the thread. "
                "If you can think of a task that would help achieve more high quality end result, then use the create_task function to create the task. "
                "Do not ever ask user confirmation for creating a task. "
                "If the request is completely processed, you do not have to create a task."
                task = AgentTask(recipient="TeamLeader", task_description=team_leader_request, requestor="user")
                self.add_task(task)

        self.dismantle_team()

    def get_by_name(self, name) -> AgentTeamMember:
        if name == "TeamLeader":
            return self.team_leader
        for member in self.members:
            if member.name == name:
                return member
        return None


def create_task(recipient: str, request: str, requestor:str) -> str:
    """
    Requests another agent in the team to complete a task.

    :param recipient (str): The name of the agent that is being requested to complete the task.
    :param request (str): A description of the to complete. This can also be a question.
    :param requestor (str): The name of the agent who is requesting the task.
    :return: True if the task was successfully received, False otherwise.
    :rtype: str
    """
    task = AgentTask(recipient=recipient, task_description=request, requestor=requestor)
    AgentTeam.instance.add_task(task)
    return "True"


# Statically defined agent team functions for fast reference
agent_team_functions = {
    "create_task": create_task,
}

functions = FunctionTool(functions=agent_team_functions)