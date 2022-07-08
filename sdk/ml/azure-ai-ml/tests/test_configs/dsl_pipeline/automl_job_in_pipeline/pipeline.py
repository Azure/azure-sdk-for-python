from azure.ai.ml import dsl, Input, command, Output
from azure.ai.ml.automl import regression
from azure.ai.ml.entities import PipelineJob
from pathlib import Path

from azure.ai.ml.entities._job.automl.tabular import TabularFeaturizationSettings

input_data_dir = str(Path(__file__).parent.parent.parent / "automl_job/test_datasets/house_pricing")


def generate_dsl_pipeline() -> PipelineJob:
    # Construct pipeline
    @dsl.pipeline(
        default_compute="cpu-cluster",
        description="Example of using automl function inside pipeline",
    )
    def automl_node_in_pipeline(
            automl_train_data,
            automl_validate_data,
            automl_test_data
    ):
        hello_automl_regression = regression(
            training_data=automl_train_data,
            validation_data=automl_validate_data,
            test_data=automl_test_data,
            target_column_name="SalePrice",
            primary_metric="r2_score",
            featurization=TabularFeaturizationSettings(mode="Off"),
            outputs={"best_model": Output(type="mlflow_model")}
        )
        hello_automl_regression.set_limits(max_trials=1, max_concurrent_trials=1)
        hello_automl_regression.set_training(
            enable_stack_ensemble=False,
            enable_vote_ensemble=False
        )

        command_func = command(
            inputs=dict(
                automl_output=Input(type="mlflow_model")
            ),
            command="ls ${{inputs.automl_output}}",
            environment="azureml:AzureML-Minimal:1"
        )
        show_output = command_func(automl_output=hello_automl_regression.outputs.best_model)
        return hello_automl_regression.outputs

    pipeline = automl_node_in_pipeline(
        automl_train_data=Input(path=input_data_dir + "/train", type="mltable"),
        automl_validate_data=Input(path=input_data_dir + "/valid", type="mltable"),
        automl_test_data=Input(path=input_data_dir + "/test", type="mltable")
    )
    return pipeline
