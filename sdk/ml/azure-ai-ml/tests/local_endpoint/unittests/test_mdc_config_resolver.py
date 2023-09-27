# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest

from azure.ai.ml._local_endpoints.mdc_config_resolver import MdcConfigResolver
from azure.ai.ml.entities._deployment.data_collector import DataCollector
from azure.ai.ml.entities._deployment.deployment_collection import DeploymentCollection
from azure.ai.ml.entities._deployment.request_logging import RequestLogging


@pytest.mark.unittest
class TestMdcConfigResolver:
    def test_resolve_mdc_config(self):
        resolver = MdcConfigResolver(
            data_collector=DataCollector(
                collections={
                    "inputs": DeploymentCollection(enabled="true", sampling_rate=0.8),
                    "outputs": DeploymentCollection(enabled="true", sampling_rate=0.7),
                    "request": DeploymentCollection(enabled="true", sampling_rate=0.6),
                    "Response": DeploymentCollection(enabled="true", sampling_rate=0.5),
                },
                request_logging=RequestLogging(capture_headers=["aaa", "bbb"]),
            )
        )

        mdc_config = {
            "collections": {
                "inputs": {"enabled": True, "sampling_percentage": 80},
                "outputs": {"enabled": True, "sampling_percentage": 70},
                "request": {"enabled": True, "sampling_percentage": 60},
                "response": {"enabled": True, "sampling_percentage": 50},
            },
            "runMode": "local",
            "captureHeaders": ["aaa", "bbb"],
        }

        assert mdc_config == resolver.mdc_config
        assert {} == resolver.environment_variables
        assert {} == resolver.volumes

    def test_resolve_mdc_config_global_sampling_rate(self):
        resolver = MdcConfigResolver(
            data_collector=DataCollector(
                collections={
                    "inputs": DeploymentCollection(enabled="true"),
                    "outputs": DeploymentCollection(enabled="true"),
                    "request": DeploymentCollection(enabled="true"),
                    "Response": DeploymentCollection(enabled="true"),
                },
                request_logging=RequestLogging(capture_headers=["aaa", "bbb"]),
                sampling_rate=0.9,
            )
        )

        mdc_config = {
            "collections": {
                "inputs": {"enabled": True, "sampling_percentage": 90},
                "outputs": {"enabled": True, "sampling_percentage": 90},
                "request": {"enabled": True, "sampling_percentage": 90},
                "response": {"enabled": True, "sampling_percentage": 90},
            },
            "runMode": "local",
            "captureHeaders": ["aaa", "bbb"],
        }

        assert mdc_config == resolver.mdc_config
        assert {} == resolver.environment_variables
        assert {} == resolver.volumes

    def test_resolve_mdc_config_collections_disabled(self):
        resolver = MdcConfigResolver(
            data_collector=DataCollector(
                collections={
                    "inputs": DeploymentCollection(enabled="false"),
                    "outputs": DeploymentCollection(enabled="false"),
                    "request": DeploymentCollection(enabled="false"),
                    "Response": DeploymentCollection(enabled="false"),
                },
                request_logging=RequestLogging(capture_headers=["aaa", "bbb"]),
                sampling_rate=0.9,
            )
        )

        assert not resolver.mdc_config
        resolver.write_file("/mnt")
        assert {} == resolver.environment_variables
        assert {} == resolver.volumes

    def test_resolve_mdc_config_no_collections(self):
        resolver = MdcConfigResolver(data_collector=DataCollector(collections={}))

        assert not resolver.mdc_config
        resolver.write_file("/mnt")
        assert {} == resolver.environment_variables
        assert {} == resolver.volumes

    def test_resolve_mdc_config_no_custom_logging(self):
        resolver = MdcConfigResolver(
            data_collector=DataCollector(
                collections={
                    "request": DeploymentCollection(enabled="true"),
                    "Response": DeploymentCollection(enabled="true"),
                },
                request_logging=RequestLogging(capture_headers=["aaa", "bbb"]),
                sampling_rate=0.9,
            )
        )

        assert not resolver.mdc_config
        resolver.write_file("/mnt")
        assert {} == resolver.environment_variables
        assert {} == resolver.volumes
