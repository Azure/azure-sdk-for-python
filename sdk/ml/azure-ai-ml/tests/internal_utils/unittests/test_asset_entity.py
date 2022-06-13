import pytest
import unittest

from azure.ai.ml.entities import Environment
from azure.ai.ml._utils.utils import is_valid_uuid


@pytest.mark.unittest
class TestAssetEntity(unittest.TestCase):
    # Using Environment because Asset class can't be instantiated directly
    def test_version_name_not_set(self) -> None:
        with pytest.raises(Exception):
            Environment(local_path=".", version="12")

    def test_version_not_str(self) -> None:
        with pytest.raises(Exception):
            Environment(name="some-name", version=1)
