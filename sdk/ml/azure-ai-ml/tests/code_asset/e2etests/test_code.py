from typing import Callable
import pytest
import uuid
from unittest.mock import patch
from pathlib import Path

from azure.ai.ml import MLClient
from test_utilities.utils import get_arm_id
from azure.ai.ml.entities._assets import Code
from azure.ai.ml._ml_exceptions import ValidationException

from devtools_testutils import AzureRecordedTestCase


@pytest.fixture
def code_asset_path(tmp_path: Path) -> str:
    code_path = tmp_path / "code.txt"
    code_path.write_text("hello world")
    return str(code_path)


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test", "mock_code_hash")
class TestCode(AzureRecordedTestCase):
    def test_create_and_get(self,
        client: MLClient,
        code_asset_path: str,
        randstr: Callable[[str], str],
    ) -> None:
        name = randstr("name")
        code_entity = Code(name=name, version="2", path=code_asset_path)
        assert str(code_entity.path) == str(Path(code_asset_path))
        code_asset_1 = client._code.create_or_update(code_entity)
        code_asset_2 = client._code.get(code_asset_1.name, code_asset_1.version)

        arm_id = get_arm_id(
            ws_scope=client._operation_scope,
            entity_name=code_asset_1.name,
            entity_version=code_asset_1.version,
            entity_type="codes",
        )
        assert code_asset_1.id == code_asset_2.id == arm_id

    def test_asset_path_update(self,
        client: MLClient,
        randstr: Callable[[str], str],
        code_asset_path: str,
    ) -> None:
        name = randstr("name")
        code_entity = Code(name=name, version="1", path=code_asset_path)

        _ = client._code.create_or_update(code_entity)

        # create same name and version code asset again with different content hash/asset paths
        with pytest.raises(Exception):
            code_entity.path = code_asset_path
            client._code.create_or_update(code_entity)

    def test_create_and_get_from_registry(
        self,
        registry_client: MLClient,
        code_asset_path: str,
        randstr: Callable[[str], str],
    ) -> None:
        name = randstr("name")
        code_entity = Code(name=name, version="2", path=code_asset_path)
        assert str(code_entity.path) == str(Path(code_asset_path))
        code_asset_1 = registry_client._code.create_or_update(code_entity)
        code_asset_2 = registry_client._code.get(code_asset_1.name, code_asset_1.version)
        assert code_asset_1.id == code_asset_2.id
