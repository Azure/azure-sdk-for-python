import os.path
import tempfile
import uuid
from pathlib import Path
from typing import Callable
from unittest.mock import patch

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import get_arm_id

from azure.ai.ml import MLClient
from azure.ai.ml.entities._assets import Code


@pytest.fixture
def code_asset_path(tmp_path: Path) -> str:
    code_path = tmp_path / "code.txt"
    code_path.write_text("hello world")
    return str(code_path)


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test", "mock_code_hash")
@pytest.mark.core_sdk_test
class TestCode(AzureRecordedTestCase):
    def test_create_and_get(self, client: MLClient, code_asset_path: str, randstr: Callable[[], str]) -> None:
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

    @pytest.mark.skip(reason="not raising exception")
    def test_asset_path_update(
        self,
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

    @pytest.mark.skipif(condition=not is_live(), reason="registry tests do not record properly. Investigate later.")
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

    def test_download_directory_code(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        with tempfile.TemporaryDirectory() as base_dir:
            # blob path is relative to the folder name of the code path.
            # to ensure that request url matches in playback mode, we need to guarantee that the folder name is the same
            source_dir = Path(base_dir, randstr("source_dir"))
            source_dir.mkdir()

            Path(source_dir, "file1.txt").write_text(randstr("content1"))
            Path(source_dir, "file2.txt").write_text(randstr("content2"))

            # code of the same content will be created only once, so we need to use name/version from created code
            code_entity = Code(name=randstr("name"), version="1", path=source_dir)
            created_code = client._code.create_or_update(code_entity)
            with tempfile.TemporaryDirectory() as target_dir:
                client._code.download(created_code.name, created_code.version, download_path=target_dir)

                assert Path(target_dir, "file1.txt").is_file()
                assert Path(target_dir, "file1.txt").read_text() == Path(source_dir, "file1.txt").read_text()
                assert Path(target_dir, "file2.txt").read_text() == Path(source_dir, "file2.txt").read_text()

    def test_download_file_code(self, client: MLClient, code_asset_path: str, randstr: Callable[[str], str]) -> None:
        code_entity = Code(name=randstr("name"), version="1", path=code_asset_path)
        # code of the same content will be created only once, so we need to use name/version from created code
        created_code = client._code.create_or_update(code_entity)
        with tempfile.TemporaryDirectory() as temp_dir:
            client._code.download(created_code.name, created_code.version, download_path=temp_dir)
            assert Path(temp_dir, "code.txt").is_file()
            assert Path(temp_dir, "code.txt").read_text() == Path(code_asset_path).read_text()
