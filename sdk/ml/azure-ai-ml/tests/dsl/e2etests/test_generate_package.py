import json
import tempfile
from itertools import islice
from unittest.mock import patch

import pytest
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD

from azure.ai.ml import MLClient
from azure.ai.ml.dsl._utils import _change_working_dir
from azure.ai.ml.operations import ComponentOperations
from mldesigner import generate
from mldesigner._generate._generate_package_impl import AssetsUtil

from .._util import _DSL_TIMEOUT_SECOND


@pytest.mark.usefixtures("enable_pipeline_private_preview_features")
@pytest.mark.timeout(timeout=_DSL_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
class TestGeneratePackage:
    def test_generate_workspace_component(
        self,
        client: MLClient,
    ):
        test_workspace_pattern = (
            AssetsUtil.WORKSPACE_FORMATTER.format(
                client._operation_scope.subscription_id,
                client._operation_scope.resource_group_name,
                client.workspace_name,
            )
            + "/components/"
        )
        # only list 10 components due to perf issue
        mock_result = islice(client.components.list(), 5)
        with patch.object(ComponentOperations, "list", return_value=mock_result):
            with tempfile.TemporaryDirectory() as temp_dir, _change_working_dir(temp_dir):
                # test list assets
                assets = [test_workspace_pattern]
                generate(source=assets)

                # test dict assets
                assets = {
                    "my/component/module1": [test_workspace_pattern],
                    "my/component/module2": [test_workspace_pattern],
                }
                generate(source=assets)

    @pytest.mark.skip(reason="TODO: 1948942, invalid registry component leads to rest client infinite loop.")
    def test_generate_registry_component(self, registry_client: MLClient):
        test_registry_pattern = (
            "azureml://registries/{}".format(
                registry_client._registry_name,
            )
            + "/components/"
        )
        mock_result = islice(registry_client.components.list(), 10)
        with patch.object(ComponentOperations, "list", return_value=mock_result):
            with tempfile.TemporaryDirectory() as temp_dir, _change_working_dir(temp_dir):
                with open("config.json", "w") as f:
                    json.dump(
                        {
                            "workspace_name": registry_client.workspace_name,
                            "resource_group": registry_client._operation_scope.resource_group_name,
                            "subscription_id": registry_client._operation_scope.subscription_id,
                        },
                        f,
                    )
                # test list assets
                assets = [test_registry_pattern]
                generate(source=assets)

                # test dict assets
                assets = {
                    "my/component/module1": [test_registry_pattern],
                    "my/component/module2": [test_registry_pattern],
                }
                generate(source=assets)
