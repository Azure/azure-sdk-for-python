# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
import personalizer_helpers_async

import personalizer_helpers


class TestLogPropertiesAsync(AzureRecordedTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy_async
    async def test_delete_log(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_multi_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_multi_slot')
        client = personalizer_helpers_async.create_async_personalizer_admin_client(
            personalizer_endpoint, personalizer_api_key)
        await client.delete_logs()
        log_properties = await client.get_log_properties()
        date_range = log_properties.get("dateRange")
        if date_range is not None:
            assert "from" in date_range
            assert date_range["from"] is None
            assert "to" in date_range
            assert date_range["to"] is None
