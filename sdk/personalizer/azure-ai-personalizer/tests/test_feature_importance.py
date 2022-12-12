# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
import personalizer_helpers
import time
from datetime import date
import uuid


class TestFeatureImportances(AzureRecordedTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy
    def test_run_feature_importance(self, **kwargs):
        variables = kwargs.pop("variables", {})
        feature_importance_id = variables.setdefault("test_run_feature_importance_id", str(uuid.uuid4()))
        personalizer_endpoint = kwargs.pop('personalizer_preset_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_preset_api_key_single_slot')
        client = personalizer_helpers.create_personalizer_admin_client(personalizer_endpoint, personalizer_api_key)
        feature_importance_name = "python_sdk_test_feature_imp"
        start_time = date.fromisoformat("2022-09-20")
        end_time = date.fromisoformat("2022-09-30")
        feature_importance_contract = {
            "name": feature_importance_name,
            "startTime": start_time,
            "endTime": end_time,
        }
        client.create_feature_importance(feature_importance_id, feature_importance_contract)
        self.wait_for_feature_importance_to_finish(client, feature_importance_id)
        feature_importance = client.get_feature_importance(feature_importance_id)
        assert feature_importance["id"] == feature_importance_id
        assert feature_importance["name"] == feature_importance_name
        assert feature_importance["status"] == "Succeeded"
        client.delete_feature_importance(feature_importance_id)
        return variables

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy
    def test_list_feature_importances(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = personalizer_helpers.create_personalizer_admin_client(personalizer_endpoint, personalizer_api_key)
        client.list_feature_importances()

    def is_feature_importance_final(self, client, feature_importance_id):
        feature_importance = client.get_feature_importance(feature_importance_id)
        return feature_importance["status"] == "Succeeded" \
               or feature_importance["status"] == "Failed" \
               or feature_importance["status"] == "Timeout" \
               or feature_importance["status"] == "Canceled"

    def wait_for_feature_importance_to_finish(self, client, feature_importance_id):
        while not self.is_feature_importance_final(client, feature_importance_id):
            self.sleep(60)

    def sleep(self, delay):
        if self.is_live:
            time.sleep(delay)
