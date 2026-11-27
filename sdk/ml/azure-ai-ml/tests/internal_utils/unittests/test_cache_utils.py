import os
import stat
import subprocess
from pathlib import Path
from typing import Union

import mock
import pytest

from azure.ai.ml import MLClient, load_job
from azure.ai.ml._utils._cache_utils import CachedNodeResolver, _CacheContent
from azure.ai.ml.entities import Component, PipelineJob


@pytest.mark.unittest
@pytest.mark.pipeline_test
@pytest.mark.usefixtures("enable_pipeline_private_preview_features", "mock_component_hash")
class TestCacheUtils:
    @staticmethod
    def _mock_resolver(component: Union[str, Component], azureml_type: str) -> str:
        if isinstance(component, str):
            return azureml_type + ":" + component if not component.startswith(azureml_type + ":") else component
        return component._get_anonymous_hash()

    @staticmethod
    def _get_cache_path(component: Component, resolver: CachedNodeResolver) -> Path:
        in_memory_hash = resolver._get_in_memory_hash_for_component(component)
        on_disk_hash = resolver.calc_on_disk_hash_for_component(component=component, in_memory_hash=in_memory_hash)
        return resolver._get_on_disk_cache_path(on_disk_hash)

    @staticmethod
    def create_resolver(client: MLClient) -> CachedNodeResolver:
        return CachedNodeResolver(
            resolver=TestCacheUtils._mock_resolver,
            client_key=client.components._get_client_key(),
        )

    @staticmethod
    def get_target_node():
        pipeline_job: PipelineJob = load_job(
            source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_inline_comps.yml",
        )
        return pipeline_job.jobs["hello_world_component_inline"]

    @staticmethod
    def register_target_node_and_resolve(resolver: CachedNodeResolver) -> None:
        # clear in-memory cache
        resolver._cache.clear()
        target_node = TestCacheUtils.get_target_node()
        # always register a newly created node
        resolver.register_node_for_lazy_resolution(target_node)
        resolver.resolve_nodes()
        return target_node.component

    @pytest.fixture
    def cache_root(self, tmp_path: Path, mocker) -> Path:
        cache_root = tmp_path / "azure-ai-ml"
        mocker.patch("azure.ai.ml._utils._cache_utils.get_base_directory_for_cache", return_value=cache_root)
        mocker.patch(
            "azure.ai.ml._utils._cache_utils.get_versioned_base_directory_for_cache",
            return_value=cache_root / "1.0.0",
        )
        return cache_root

    def test_on_disk_cache_occupied(self, mock_machinelearning_client: MLClient, cache_root: Path, mocker) -> None:
        mocker.patch("azure.ai.ml._utils._cache_utils.ensure_private_directory", return_value=True)
        resolver = self.create_resolver(mock_machinelearning_client)
        target_cache_path = self._get_cache_path(self.get_target_node().component, resolver)
        assert not target_cache_path.exists()
        self.register_target_node_and_resolve(resolver)
        assert target_cache_path.exists()
        os.chmod(target_cache_path, stat.S_IREAD)

        # test write to readonly file
        # mock to avoid using existed on-disk cache
        with mock.patch.object(resolver, "_load_from_on_disk_cache", return_value=None):
            cur_time = os.stat(target_cache_path).st_mtime
            self.register_target_node_and_resolve(resolver)
            # no change to the file and no exception raised
            assert cur_time == os.stat(target_cache_path).st_mtime

    @pytest.mark.skipif(os.name == "nt", reason="POSIX file permissions are not used on Windows")
    def test_on_disk_cache_is_private(self, mock_machinelearning_client: MLClient, cache_root: Path) -> None:
        resolver = self.create_resolver(mock_machinelearning_client)
        target_cache_path = self._get_cache_path(self.get_target_node().component, resolver)

        self.register_target_node_and_resolve(resolver)
        assert target_cache_path.exists()
        assert stat.S_IMODE(target_cache_path.stat().st_mode) == 0o600
        assert cache_root.stat().st_uid == os.getuid()
        assert stat.S_IMODE(cache_root.stat().st_mode) == 0o700

    def test_on_disk_cache_ignored_when_cache_root_is_not_private(
        self, mock_machinelearning_client: MLClient, cache_root: Path, mocker
    ) -> None:
        resolver = self.create_resolver(mock_machinelearning_client)
        target_component = self.get_target_node().component
        target_cache_path = self._get_cache_path(target_component, resolver)
        untrusted_arm_id = "azureml:/subscriptions/other/components/untrusted/versions/1"
        target_cache_path.parent.mkdir(parents=True, exist_ok=True)
        target_cache_path.write_text(untrusted_arm_id, encoding="utf-8")
        mocker.patch("azure.ai.ml._utils._cache_utils.ensure_private_directory", return_value=False)
        update_on_disk_hash = mocker.spy(_CacheContent, "update_on_disk_hash")

        assert self.register_target_node_and_resolve(resolver) == target_component._get_anonymous_hash()
        assert target_cache_path.read_text(encoding="utf-8") == untrusted_arm_id
        update_on_disk_hash.assert_not_called()

    def test_on_disk_cache_uses_the_directory_it_checked(
        self, mock_machinelearning_client: MLClient, cache_root: Path, tmp_path: Path, mocker
    ) -> None:
        mocker.patch("azure.ai.ml._utils._cache_utils.ensure_private_directory", return_value=True)
        resolver = self.create_resolver(mock_machinelearning_client)
        target_component = self.get_target_node().component
        target_cache_path = self._get_cache_path(target_component, resolver)
        self.register_target_node_and_resolve(resolver)
        assert target_cache_path.exists()

        # The base directory changes after the cache was checked, for example because the temporary directory changed.
        other_root = tmp_path / "other"
        mocker.patch("azure.ai.ml._utils._cache_utils.get_base_directory_for_cache", return_value=other_root)
        mocker.patch(
            "azure.ai.ml._utils._cache_utils.get_versioned_base_directory_for_cache",
            return_value=other_root / "1.0.0",
        )
        other_cache_path = other_root / "1.0.0" / "components" / resolver._client_hash / target_cache_path.name
        other_cache_path.parent.mkdir(parents=True)
        other_cache_path.write_text("azureml:/subscriptions/other/components/untrusted/versions/1", encoding="utf-8")

        assert self.register_target_node_and_resolve(resolver) == target_component._get_anonymous_hash()
        assert self._get_cache_path(target_component, resolver) == target_cache_path

    def test_on_disk_cache_ignored_when_cache_directory_is_redirected(
        self, mock_machinelearning_client: MLClient, cache_root: Path, tmp_path: Path, mocker
    ) -> None:
        shared_directory = tmp_path / "shared"
        cache_root.mkdir()
        shared_directory.mkdir()
        link = cache_root / "1.0.0"
        if os.name == "nt":
            # Junctions don't need the extra privileges that symlinks need on Windows.
            subprocess.run(
                [os.environ["COMSPEC"], "/c", "mklink", "/J", str(link), str(shared_directory)],
                check=True,
                capture_output=True,
            )
        else:
            link.symlink_to(shared_directory, target_is_directory=True)
        mocker.patch("azure.ai.ml._utils._cache_utils.ensure_private_directory", return_value=True)
        resolver = self.create_resolver(mock_machinelearning_client)
        target_component = self.get_target_node().component

        assert self.register_target_node_and_resolve(resolver) == target_component._get_anonymous_hash()
        assert not list(shared_directory.iterdir())
