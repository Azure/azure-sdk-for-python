import os
import stat
from pathlib import Path
from typing import Union

import mock
import pytest

from azure.ai.ml import MLClient, load_job
from azure.ai.ml._utils._cache_utils import CachedNodeResolver
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

    def test_on_disk_cache_occupied(self, mock_machinelearning_client: MLClient) -> None:
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

    def test_on_disk_cache_share_among_users(self, mock_machinelearning_client: MLClient) -> None:
        resolver = self.create_resolver(mock_machinelearning_client)
        target_cache_path = self._get_cache_path(self.get_target_node().component, resolver)

        self.register_target_node_and_resolve(resolver)
        assert target_cache_path.exists()
        assert stat.filemode(target_cache_path.stat().st_mode) == "-rw-rw-rw-"
