# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
import personalizer_helpers_async
import asyncio
from datetime import date
import uuid

import personalizer_helpers

class TestFeatureImportancesAsync(AzureRecordedTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy_async
    async def test_run_feature_importance(self, **kwargs):
        variables = kwargs.pop("variables", {})
        feature_importance_id = variables.setdefault("test_run_feature_importance_async_id", str(uuid.uuid4()))
        personalizer_endpoint = kwargs.pop('personalizer_preset_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_preset_api_key_single_slot')
        client = personalizer_helpers_async.create_async_personalizer_admin_client(
            personalizer_endpoint, personalizer_api_key)
        feature_importance_name = "python_sdk_test_feature_imp"
        start_time = date.fromisoformat("2022-09-20")
        end_time = date.fromisoformat("2022-09-30")
        feature_importance_contract = {
            "name": feature_importance_name,
            "startTime": start_time,
            "endTime": end_time,
        }
        await client.create_feature_importance(feature_importance_id, feature_importance_contract)
        await self.wait_for_feature_importance_to_finish(client, feature_importance_id)
        feature_importance = await client.get_feature_importance(feature_importance_id)
        assert feature_importance["id"] == feature_importance_id
        assert feature_importance["name"] == feature_importance_name
        assert feature_importance["status"] == "Succeeded"
        await client.delete_feature_importance(feature_importance_id)
        return variables

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy_async
    async def test_list_feature_importances(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = personalizer_helpers_async.create_async_personalizer_admin_client(
            personalizer_endpoint, personalizer_api_key)
        client.list_feature_importances()

    async def is_feature_importance_final(self, client, feature_importance_id):
        feature_importance = await client.get_feature_importance(feature_importance_id)
        return feature_importance["status"] == "Succeeded" \
               or feature_importance["status"] == "Failed" \
               or feature_importance["status"] == "Timeout" \
               or feature_importance["status"] == "Canceled"

    async def wait_for_feature_importance_to_finish(self, client, feature_importance_id):
        while not await self.is_feature_importance_final(client, feature_importance_id):
            await self.sleep(60)

    async def sleep(self, delay):
        if self.is_live:
            await asyncio.sleep(delay)
