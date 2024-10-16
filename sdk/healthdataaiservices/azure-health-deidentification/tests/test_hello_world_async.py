from deid_base_test_case import DeidBaseTestCase, RealtimeEnv
from devtools_testutils.aio import (
    recorded_by_proxy_async,
)
import pytest

from azure.health.deidentification.models import *


class TestHealthDeidentificationHelloWorld(DeidBaseTestCase):
    @RealtimeEnv()
    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_hello_world_async(self, healthdataaiservices_deid_service_endpoint):
        client = self.make_client_async(healthdataaiservices_deid_service_endpoint)
        assert client is not None

        content = DeidentificationContent(
            input_text="Hello, my name is John Smith.",
            operation=OperationType.SURROGATE,
            data_type=DocumentDataType.PLAINTEXT,
        )

        result: DeidentificationResult = await client.deidentify(content)

        assert result is not None
        assert result.output_text is not None
        assert result.tagger_result is None

        assert result.output_text.startswith("Hello, my name is ")
        assert "John Smith" not in result.output_text
        assert "[" not in result.output_text
