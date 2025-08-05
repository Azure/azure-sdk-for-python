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
    async def test_hello_world(self, healthdataaiservices_deid_service_endpoint):
        client = self.make_client_async(healthdataaiservices_deid_service_endpoint)
        assert client is not None

        tagged_entities: TaggedPhiEntities = TaggedPhiEntities(
            encoding=TextEncodingType.CODE_POINT,
            entities=[SimplePhiEntity(category=PhiCategory.PATIENT, offset=18, length=10)],
        )

        content = DeidentificationContent(
            input_text="Hello, my name is John Smith.",
            operation_type=DeidentificationOperationType.SURROGATE_ONLY,
            tagged_entities=tagged_entities,
        )

        result: DeidentificationResult = await client.deidentify_text(content)

        assert result is not None
        assert result.output_text is not None
        assert result.tagger_result is None

        assert result.output_text.startswith("Hello, my name is ")
        assert "John Smith" not in result.output_text
        assert "[" not in result.output_text
