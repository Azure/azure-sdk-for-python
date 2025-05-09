from typing import List

from azure.ai.evaluation import AIAgentConverter
from azure.ai.evaluation._common._experimental import experimental

@experimental
class FDPAgentConverter(AIAgentConverter):

    def __init__(self, **kwargs):
        super(FDPAgentConverter, self).__init__(**kwargs)

    def _list_messages_chronological(self, thread_id: str):
        """
        Lists messages in chronological order for a given thread.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :return: A list of messages in chronological order.
        """
        message_iter = self.project_client.agents.messages.list(
            thread_id=thread_id, limit=self._AI_SERVICES_API_MAX_LIMIT, order="asc"
        )
        return [message for message in message_iter]

    def _list_run_steps_chronological(self, thread_id: str, run_id: str):

        return  self.project_client.agents.run_steps.list(
                thread_id=thread_id,
                run_id=run_id,
                limit=self._AI_SERVICES_API_MAX_LIMIT,
                order="asc"
            )

    def _list_run_ids_chronological(self, thread_id: str) -> List[str]:
        runs = self.project_client.agents.runs.list(thread_id=thread_id, order="asc")
        return [run.id for run in runs]

    def _get_run(self, thread_id: str, run_id: str):
        return self.project_client.agents.runs.get(thread_id=thread_id, run_id=run_id)