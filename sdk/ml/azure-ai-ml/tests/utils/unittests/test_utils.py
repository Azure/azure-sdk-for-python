import pytest

from azure.ai.ml._utils.utils import from_iso_duration_format_min_sec


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestUtils:
    def test_from_iso_duration_format_min_sec(self) -> None:
        duration = from_iso_duration_format_min_sec("PT10M41.7894561S")
        assert duration == "10m 41s"
