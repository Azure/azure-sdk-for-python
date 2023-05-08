# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json

import pytest

from azure.ai.ml._local_endpoints.mdc_config_resolver import MdcConfigResolver
from azure.ai.ml.entities._deployment.data_collector import DataCollector
from azure.ai.ml.entities._deployment.deployment_collection import DeploymentCollection


@pytest.mark.unittest
class TestMdcConfigResolver:
    def test_resolve_mdc_config(self):
        resolver = MdcConfigResolver(
            data_collector=DataCollector(
                collections={
                    "inputs": DeploymentCollection(enabled=True),
                    "outputs": DeploymentCollection(enabled=True),
                }
            )
        )

        print(json.dumps(resolver.mdc_config))
