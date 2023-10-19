import pytest

from azure.ai.resources import AIClient


@pytest.mark.e2etest
class TestBasic:
    def test_basic(self, ai_client: AIClient):

        # Connection override is not working yet
        run = ai_client.pf.batch_run(flow="./samples/flows/web_classification",
                                     data="./samples/flows/webClassification3.jsonl",
                                     inputs_mapping={"url": "${data.url}"},
                                     runtime="hancwang3-default")

        result = ai_client.pf.get_run_details(run["name"])
        print(result)
