import unittest

import pytest

from azure.ai.ml._utils.utils import is_valid_uuid
from azure.ai.ml.entities import Environment


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestAssetEntity(unittest.TestCase):
    # Using Environment because Asset class can't be instantiated directly
    def test_version_name_not_set(self) -> None:
        with pytest.raises(Exception):
            Environment(local_path=".", version="12")

    def test_version_not_str(self) -> None:
        with pytest.raises(Exception):
            Environment(name="some-name", version=1)
