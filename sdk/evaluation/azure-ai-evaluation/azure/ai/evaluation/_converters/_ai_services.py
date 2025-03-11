from azure.ai.projects import AIProjectClient


class AIAgentConverter:
    def __init__(self, project_client: AIProjectClient):
        self.project_client = project_client

    # Get system messages
    def get_instructions(self, thread_id: str, run_id: str):
        # What if they use system messages instead?
        return self.project_client.agents.get_run(thread_id=thread_id, run_id=run_id).instructions

    # conversation history up to but not including the current run
    def get_conversation_history(self, thread_id: str, run_id: str):
        messages = self.project_client.agents.list_messages(thread_id=thread_id)
        ret = []
        for message in messages.data[::-1]:
            if message.run_id == run_id:
                break
            if message.role in ["user", "assistant"]:
                # theoretically there can be more than one system message
                # we are not handling if they are interspersed with user/assistant messages
                # just take them all before the current run
                ret.append(message)
        return ret

    # agent response for current run
    def get_agent_response(self, thread_id: str, run_id: str):
        return [message for message in self.project_client.agents.list_messages(thread_id=thread_id, run_id=run_id).data if message.run_id == run_id]

    # tool definitions for current run
    def get_tool_definitions(self, thread_id: str, run_id: str):
        return self.project_client.agents.get_run(thread_id=thread_id, run_id=run_id).tools

    def convert(self, thread_id: str, run_id: str):
        instructions = self.get_instructions(thread_id, run_id)
        history = self.get_conversation_history(thread_id, run_id)
        agent_response = self.get_agent_response(thread_id, run_id)
        tool_definitions = self.get_tool_definitions(thread_id, run_id)
        return {
            "instructions": instructions,
            "history": history,
            "agent_response": agent_response,
            "tool_definitions": tool_definitions
        }