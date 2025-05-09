from typing import List

from azure.ai.evaluation import AIAgentConverter
from azure.ai.evaluation._common._experimental import experimental

@experimental
class LegacyAgentConverter(AIAgentConverter):

    def __init__(self, **kwargs):
        super(LegacyAgentConverter, self).__init__(**kwargs)

    def _list_messages_chronological(self, thread_id: str):
        """
        Lists messages in chronological order for a given thread.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :return: A list of messages in chronological order.
        """
        to_return = []

        has_more = True
        after = None
        while has_more:
            messages = self.project_client.agents.list_messages(
            thread_id=thread_id, limit=self._AI_SERVICES_API_MAX_LIMIT, order="asc", after=after)
            has_more = messages.has_more
            after = messages.last_id
            if messages.data:
                # We need to add the messages to the accumulator.
                to_return.extend(messages.data)

        return to_return

    def _list_run_steps_chronological(self, thread_id: str, run_id: str):
        run_steps_chronological: List[object] = []
        has_more = True
        after = None
        while has_more:
            run_steps = self.project_client.agents.list_run_steps(
                thread_id=thread_id,
                run_id=run_id,
                limit=self._AI_SERVICES_API_MAX_LIMIT,
                order="asc",
                after=after,
            )
            has_more = run_steps.has_more
            after = run_steps.last_id
            if run_steps.data:
                # We need to add the run steps to the accumulator.
                run_steps_chronological.extend(run_steps.data)
        return run_steps_chronological

    def _list_run_ids_chronological(self, thread_id: str) -> List[str]:
        """
        Lists run IDs in chronological order for a given thread.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :return: A list of run IDs in chronological order.
        :rtype: List[str]
        """
        runs = self.project_client.agents.list_runs(thread_id=thread_id, order="asc")
        run_ids = [run["id"] for run in runs["data"]]
        return run_ids

    def _get_run(self, thread_id: str, run_id: str):
        return self.project_client.agents.get_run(thread_id=thread_id, run_id=run_id)