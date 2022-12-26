# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
import personalizer_helpers
import time
from datetime import date
import uuid


class TestEvaluations(AzureRecordedTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy
    def test_run_evaluation(self, **kwargs):
        variables = kwargs.pop("variables", {})
        evaluation_id = variables.setdefault("test_run_evaluation_id", str(uuid.uuid4()))
        personalizer_endpoint = kwargs.pop('personalizer_preset_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_preset_api_key_single_slot')
        client = personalizer_helpers.create_personalizer_admin_client(personalizer_endpoint, personalizer_api_key)
        evaluation_name = "python_sdk_test_evaluation"
        start_time = date.fromisoformat("2022-09-20")
        end_time = date.fromisoformat("2022-09-30")
        iso_start_time = start_time.strftime("%Y%m%dT%H%M%S")
        iso_end_time = end_time.strftime("%Y%m%dT%H%M%S")
        evaluation_contract = {
            "name": evaluation_name,
            "startTime": start_time,
            "endTime": end_time,
            "enableOfflineExperimentation": True,
            "policies": [],
        }
        client.create_evaluation(evaluation_id, evaluation_contract)
        self.wait_for_evaluation_to_finish(client, evaluation_id, iso_start_time, iso_end_time)
        evaluation = client.get_evaluation(evaluation_id, start_time=iso_start_time, end_time=iso_end_time)
        assert evaluation["id"] == evaluation_id
        assert evaluation["name"] == evaluation_name
        assert evaluation["status"] == "Succeeded"
        client.delete_evaluation(evaluation_id)
        return variables

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy
    def test_list_evaluations(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = personalizer_helpers.create_personalizer_admin_client(personalizer_endpoint, personalizer_api_key)
        client.list_evaluations()

    def is_evaluation_final(self, client, evaluation_id, iso_start_time, iso_end_time):
        evaluation = client.get_evaluation(evaluation_id, start_time=iso_start_time, end_time=iso_end_time)
        return evaluation["status"] == "Succeeded" \
               or evaluation["status"] == "Failed" \
               or evaluation["status"] == "Timeout" \
               or evaluation["status"] == "Canceled"

    def wait_for_evaluation_to_finish(self, client, evaluation_id, iso_start_time, iso_end_time):
        while not self.is_evaluation_final(client, evaluation_id, iso_start_time, iso_end_time):
            self.sleep(60)

    def sleep(self, delay):
        if self.is_live:
            time.sleep(delay)
