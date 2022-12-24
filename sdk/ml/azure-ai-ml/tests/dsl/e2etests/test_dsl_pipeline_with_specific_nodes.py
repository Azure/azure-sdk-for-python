from pathlib import Path
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD, assert_job_cancel

from azure.ai.ml import (
    Input,
    MLClient,
    dsl,
    load_component,
)
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities import CommandComponent, Command, Choice, Sweep
from azure.ai.ml.entities import PipelineJob

from .._util import _DSL_TIMEOUT_SECOND

tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"
job_input = Input(
    type=AssetTypes.URI_FILE,
    path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
)
experiment_name = "dsl_pipeline_e2e"
common_omit_fields = [
    "properties",
    "display_name",
    "experiment_name",
    "jobs.*.componentId",
    "inputs.*.uri",
    "jobs.*._source",
    "jobs.*.properties",
    "settings._source",
    "source_job_id",
    "services",
]


@pytest.mark.usefixtures(
    "enable_environment_id_arm_expansion",
    "enable_pipeline_private_preview_features",
    "mock_code_hash",
    "mock_component_hash",
    "recorded_test",
)
@pytest.mark.timeout(timeout=_DSL_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestDSLPipelineWithSpecificNodes(AzureRecordedTestCase):
    def test_dsl_pipeline_sweep_node(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline
        def train_with_sweep_in_pipeline(raw_data, primary_metric: str = "AUC", max_total_trials: int = 10):
            component_to_sweep: CommandComponent = load_component(source=yaml_file)
            # to check the logic to set default display name for components
            component_to_sweep.display_name = None

            cmd_node1: Command = component_to_sweep(
                component_in_number=Choice([2, 3, 4, 5]), component_in_path=raw_data
            )

            sweep_job1: Sweep = cmd_node1.sweep(
                primary_metric="AUC",  # primary_metric,
                goal="maximize",
                sampling_algorithm="random",
            )
            sweep_job1.compute = "gpu-cluster"
            sweep_job1.set_limits(max_total_trials=10)  # max_total_trials

            cmd_node2: Command = component_to_sweep(
                component_in_number=Choice([2, 3, 4, 5]), component_in_path=raw_data
            )
            sweep_job2: Sweep = cmd_node2.sweep(
                primary_metric="AUC",
                goal="minimize",
                sampling_algorithm="random",
                max_total_trials=10,
            )
            sweep_job2.compute = "gpu-cluster"

            sweep_job3: Sweep = component_to_sweep(
                component_in_number=Choice([2, 3, 4, 5]), component_in_path=raw_data
            ).sweep(
                primary_metric="accuracy",
                goal="maximize",
                sampling_algorithm="random",
                max_total_trials=10,
            )

            component_to_link = load_component(source=yaml_file, params_override=[{"name": "node_to_link"}])
            link_node = component_to_link(
                component_in_number=2, component_in_path=sweep_job1.outputs.component_out_path
            )

            return {
                "pipeline_job_best_model1": sweep_job1.outputs.component_out_path,
                "pipeline_job_best_model2": sweep_job2.outputs.component_out_path,
                "pipeline_job_best_model3": sweep_job3.outputs.component_out_path,
                "pipeline_model_test_result": link_node.outputs.component_out_path,
            }

        pipeline: PipelineJob = train_with_sweep_in_pipeline(
            raw_data=job_input, max_total_trials=100, primary_metric="accuracy"
        )
        pipeline.settings.default_compute = "cpu-cluster"
        created_pipeline = assert_job_cancel(pipeline, client)
        name, version = created_pipeline.jobs["sweep_job1"].trial.split(":")
        created_component = client.components.get(name, version)
        assert created_component.display_name == "sweep_job1"
