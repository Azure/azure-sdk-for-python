import pytest
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
import personalizer_helpers
import time
from datetime import date
import uuid


class TestEvaluations(AzureRecordedTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    @pytest.mark.skip('Get evaluation api is currently failing')
    @recorded_by_proxy
    def test_run_evaluation(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = personalizer_helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        evaluation_id = str(uuid.uuid4())
        evaluation_name = "python_sdk_test_evaluation"
        start_time = date.fromisoformat("2022-09-24")
        end_time = date.fromisoformat("2022-09-26")
        iso_start_time = start_time.strftime("%Y%m%dT%H%M%S")
        iso_end_time = end_time.strftime("%Y%m%dT%H%M%S")
        evaluation_contract = {
            "name": evaluation_name,
            "startTime": start_time,
            "endTime": end_time,
            "enableOfflineExperimentation": True,
            "policies": [],
        }
        client.evaluations.create(evaluation_id, evaluation_contract)
        self.wait_for_evaluation_to_finish(client, evaluation_id, iso_start_time, iso_end_time)
        evaluation = client.evaluations.get(evaluation_id, start_time=iso_start_time, end_time=iso_end_time)
        assert evaluation["id"] == evaluation_id
        assert evaluation["name"] == evaluation_name
        assert evaluation["status"] == "Completed"
        client.evaluations.delete(evaluation_id)

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy
    def test_list_evaluations(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client =  personalizer_helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        client.evaluations.list()

    def is_evaluation_final(self, client, evaluation_id, iso_start_time, iso_end_time):
        evaluation = client.evaluations.get(evaluation_id, start_time=iso_start_time, end_time=iso_end_time)
        return evaluation["status"] == "Completed" \
               or evaluation["status"] == "Failed" \
               or evaluation["status"] == "Timeout"

    def wait_for_evaluation_to_finish(self, client, evaluation_id, iso_start_time, iso_end_time):
        while not self.is_evaluation_final(client, evaluation_id, iso_start_time, iso_end_time):
            self.sleep(60)

    def sleep(self, delay):
        if self.is_live:
            time.sleep(delay)
