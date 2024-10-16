from deid_base_test_case import DeidBaseTestCase, RealtimeEnv
from devtools_testutils import (
    recorded_by_proxy,
)
import pytest

from azure.health.deidentification.models import *


class TestHealthDeidentificationHelloWorld(DeidBaseTestCase):
    @RealtimeEnv()
    @recorded_by_proxy
    def test_hello_world(self, healthdataaiservices_deid_service_endpoint):
        client = self.make_client(healthdataaiservices_deid_service_endpoint)
        assert client is not None

        content = DeidentificationContent(
            input_text="Hello, my name is John Smith.",
            operation=OperationType.SURROGATE,
            data_type=DocumentDataType.PLAINTEXT,
        )

        result: DeidentificationResult = client.deidentify(content)

        assert result is not None
        assert result.output_text is not None
        assert result.tagger_result is None

        assert result.output_text.startswith("Hello, my name is ")
        assert "John Smith" not in result.output_text
        assert "[" not in result.output_text
