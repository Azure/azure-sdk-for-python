from pathlib import Path
from azure.ai.ml import dsl, Input, load_component, Output, command
from azure.ai.ml.constants import InputOutputModes
from azure.ai.ml.entities import PipelineJob

parent_dir = str(Path(__file__).parent)

# Load component funcs
train_func = load_component(path=parent_dir + "/train.yml")


def pipeline_without_setting_binding_node() -> PipelineJob:
    @dsl.pipeline(
        compute="cpu-cluster",
    )
    def e2e_local_components(
        training_input,
        training_max_epochs=20,
        training_learning_rate=1.8,
        learning_rate_schedule="time-based",
    ):
        """E2E dummy pipeline with components defined via yaml."""
        train_with_sample_data = train_func(
            training_data=training_input,
            max_epochs=training_max_epochs,
            learning_rate=training_learning_rate,
            learning_rate_schedule=learning_rate_schedule,
        )

        return {
            "trained_model": train_with_sample_data.outputs.model_output,
        }

    pipeline_job = e2e_local_components(
        training_input=Input(type="uri_folder", path=parent_dir + "/data/"),
    )
    return pipeline_job


def pipeline_with_only_setting_pipeline_level() -> PipelineJob:
    @dsl.pipeline(
        compute="cpu-cluster",
    )
    def e2e_local_components(
        training_input,
        training_max_epochs=20,
        training_learning_rate=1.8,
        learning_rate_schedule="time-based",
    ):
        """E2E dummy pipeline with components defined via yaml."""
        train_with_sample_data = train_func(
            training_data=training_input,
            max_epochs=training_max_epochs,
            learning_rate=training_learning_rate,
            learning_rate_schedule=learning_rate_schedule,
        )

        return {
            "trained_model": train_with_sample_data.outputs.model_output,
        }

    pipeline_job = e2e_local_components(
        training_input=Input(type="uri_folder", path=parent_dir + "/data/", mode=InputOutputModes.RO_MOUNT),
    )
    pipeline_job.outputs.trained_model.mode = InputOutputModes.UPLOAD
    return pipeline_job


def pipeline_with_only_setting_binding_node() -> PipelineJob:
    @dsl.pipeline(
        compute="cpu-cluster",
    )
    def e2e_local_components(
        training_input,
        training_max_epochs=20,
        training_learning_rate=1.8,
        learning_rate_schedule="time-based",
    ):
        """E2E dummy pipeline with components defined via yaml."""
        train_with_sample_data = train_func(
            training_data=training_input,
            max_epochs=training_max_epochs,
            learning_rate=training_learning_rate,
            learning_rate_schedule=learning_rate_schedule,
        )

        train_with_sample_data.inputs.training_data.mode = InputOutputModes.RO_MOUNT
        train_with_sample_data.outputs.model_output.mode = InputOutputModes.UPLOAD

        return {
            "trained_model": train_with_sample_data.outputs.model_output,
        }

    pipeline_job = e2e_local_components(
        training_input=Input(type="uri_folder", path=parent_dir + "/data/"),
    )
    return pipeline_job


def pipeline_with_setting_binding_node_and_pipeline_level() -> PipelineJob:
    @dsl.pipeline(
        compute="cpu-cluster",
    )
    def e2e_local_components(
        training_input,
        training_max_epochs=20,
        training_learning_rate=1.8,
        learning_rate_schedule="time-based",
    ):
        """E2E dummy pipeline with components defined via yaml."""
        train_with_sample_data = train_func(
            training_data=training_input,
            max_epochs=training_max_epochs,
            learning_rate=training_learning_rate,
            learning_rate_schedule=learning_rate_schedule,
        )

        train_with_sample_data.inputs.training_data.mode = InputOutputModes.RO_MOUNT
        train_with_sample_data.outputs.model_output.mode = InputOutputModes.UPLOAD

        return {
            "trained_model": train_with_sample_data.outputs.model_output,
        }

    pipeline_job = e2e_local_components(
        training_input=Input(type="uri_folder", path=parent_dir + "/data/", mode=InputOutputModes.DOWNLOAD),
    )
    pipeline_job.outputs.trained_model.mode = InputOutputModes.RW_MOUNT
    return pipeline_job


def pipeline_with_command_builder_setting_binding_node_and_pipeline_level() -> PipelineJob:
    environment = "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5"

    inputs = {
        "training_data": Input(type="uri_folder"),
        "max_epochs": 20,
        "learning_rate": 1.8,
        "learning_rate_schedule": "time-based",
    }
    outputs = {"model_output": Output(type="uri_folder")}
    train_func = command(
        environment=environment,
        command='echo "hello world"',
        distribution={"type": "Pytorch", "process_count_per_instance": 2},
        inputs=inputs,
        outputs=outputs,
    )

    @dsl.pipeline(
        compute="cpu-cluster",
    )
    def e2e_local_components(
        training_input,
        training_max_epochs=20,
        training_learning_rate=1.8,
        learning_rate_schedule="time-based",
    ):
        """E2E dummy pipeline with components defined via yaml."""
        train_with_sample_data = train_func(
            training_data=training_input,
            max_epochs=training_max_epochs,
            learning_rate=training_learning_rate,
            learning_rate_schedule=learning_rate_schedule,
        )

        train_with_sample_data.inputs.training_data.mode = InputOutputModes.RO_MOUNT
        train_with_sample_data.outputs.model_output.mode = InputOutputModes.UPLOAD

        return {
            "trained_model": train_with_sample_data.outputs.model_output,
        }

    pipeline_job = e2e_local_components(
        training_input=Input(type="uri_folder", path=parent_dir + "/data/", mode=InputOutputModes.DOWNLOAD),
    )
    pipeline_job.outputs.trained_model.mode = InputOutputModes.RW_MOUNT
    return pipeline_job


def nested_dsl_pipeline_with_setting_binding_node_and_pipeline_level() -> PipelineJob:
    @dsl.pipeline(
        name="pipeline_component",
    )
    def pipeline_component_func(
        training_input: Input(type="uri_file", mode=InputOutputModes.DOWNLOAD),
        training_max_epocs: int,
        training_learning_rate: float,
        learning_rate_schedule: str,
    ) -> Output(mode=InputOutputModes.RW_MOUNT):

        train_job = train_func(
            training_data=training_input,
            max_epochs=training_max_epocs,
            learning_rate=training_learning_rate,
            learning_rate_schedule=learning_rate_schedule,
        )
        train_job.inputs.training_data.mode = InputOutputModes.MOUNT
        train_job.outputs.model_output.mode = InputOutputModes.MOUNT
        return {
            "trained_model": train_job.outputs.model_output,
        }

    @dsl.pipeline(
        compute="cpu-cluster",
    )
    def e2e_local_components(
        pipeline_training_input,
        pipeline_training_max_epochs=20,
        pipeline_training_learning_rate=1.8,
        pipeline_learning_rate_schedule="time-based",
    ):
        """E2E dummy pipeline with components defined via yaml."""
        subgraph1 = pipeline_component_func(
            training_input=pipeline_training_input,
            training_max_epocs=pipeline_training_max_epochs,
            training_learning_rate=pipeline_training_learning_rate,
            learning_rate_schedule=pipeline_learning_rate_schedule,
        )
        subgraph1.inputs.training_input.mode = InputOutputModes.RO_MOUNT
        subgraph1.outputs.trained_model.mode = InputOutputModes.UPLOAD

        return {
            "pipeline_trained_model": subgraph1.outputs.trained_model,
        }

    pipeline_job = e2e_local_components(
        pipeline_training_input=Input(type="uri_folder", path=parent_dir + "/data/", mode=InputOutputModes.DOWNLOAD),
    )
    pipeline_job.outputs.pipeline_trained_model.mode = InputOutputModes.RW_MOUNT
    return pipeline_job
