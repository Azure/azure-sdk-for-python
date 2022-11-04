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


class TestEvaluationsAsync(AzureRecordedTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy_async
    async def test_run_evaluation(self, **kwargs):
        variables = kwargs.pop("variables", {})
        evaluation_id = variables.setdefault("test_run_evaluation_async_id", str(uuid.uuid4()))
        personalizer_endpoint = kwargs.pop('personalizer_preset_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_preset_api_key_single_slot')
        client = personalizer_helpers_async.create_async_personalizer_admin_client(
            personalizer_endpoint, personalizer_api_key)
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
        await client.create_evaluation(evaluation_id, evaluation_contract)
        await self.wait_for_evaluation_to_finish(client, evaluation_id, iso_start_time, iso_end_time)
        evaluation = await client.get_evaluation(evaluation_id, start_time=iso_start_time, end_time=iso_end_time)
        assert evaluation["id"] == evaluation_id
        assert evaluation["name"] == evaluation_name
        assert evaluation["status"] == "Succeeded"
        await client.delete_evaluation(evaluation_id)
        return variables

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy_async
    async def test_list_evaluations(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = personalizer_helpers_async.create_async_personalizer_admin_client(
            personalizer_endpoint, personalizer_api_key)
        client.list_evaluations()

    async def is_evaluation_final(self, client, evaluation_id, iso_start_time, iso_end_time):
        evaluation = await client.get_evaluation(evaluation_id, start_time=iso_start_time, end_time=iso_end_time)
        return evaluation["status"] == "Succeeded" \
               or evaluation["status"] == "Failed" \
               or evaluation["status"] == "Timeout" \
               or evaluation["status"] == "Canceled"

    async def wait_for_evaluation_to_finish(self, client, evaluation_id, iso_start_time, iso_end_time):
        while not await self.is_evaluation_final(client, evaluation_id, iso_start_time, iso_end_time):
            await self.sleep(60)

    async def sleep(self, delay):
        if self.is_live:
            await asyncio.sleep(delay)
