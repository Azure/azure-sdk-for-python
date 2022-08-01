import pydash
import pytest

from azure.ai.ml import load_component, Input, dsl
from azure.ai.ml.entities._job.pipeline._exceptions import UserErrorException

from mldesigner import reference_component
from .._util import _DSL_TIMEOUT_SECOND


@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
class TestReferenceComponent:
    def test_reference_local_component(self, hello_world_component_reference):
        test_path = "./tests/test_configs/components/helloworld_component.yml"
        hello_world_load_component = load_component(path=test_path)
        node1 = hello_world_component_reference(component_in_path=Input(path="/a/path/on/ds"), component_in_number=1)
        node2 = hello_world_load_component(component_in_path=Input(path="/a/path/on/ds"), component_in_number=1)

        rest_node1 = node1._to_rest_object()
        rest_node2 = node2._to_rest_object()

        assert rest_node1 == rest_node2

    def test_reference_parallel_component(self, batch_inference_component_reference):
        test_path = "./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/score.yml"
        batch_inference_load_component = load_component(path=test_path)

        node1 = batch_inference_load_component(job_data_path=Input(path="/a/path/on/ds"))
        node2 = batch_inference_component_reference(job_data_path=Input(path="/a/path/on/ds"))

        rest_node1 = node1._to_rest_object()
        rest_node2 = node2._to_rest_object()

        assert rest_node1 == rest_node2

    def test_reference_component_config_overwrite(self):
        # TODO(1831493): support component loader
        pass

    def test_reference_local_component_illegal(self, hello_world_component_reference):
        with pytest.raises(UserErrorException) as e:
            hello_world_component_reference(Input(path="/a/path/on/ds"), 1)
        assert "`reference_component` wrapped function only accept keyword parameters." in str(e.value)

        with pytest.raises(TypeError) as e:
            hello_world_component_reference(unknown_field=1)
        assert "hello_world() got an unexpected keyword argument 'unknown_field'" in str(e.value)

        @reference_component(name="my_component")
        def illegal_return_annotation() -> int:
            ...

        with pytest.raises(UserErrorException) as e:
            illegal_return_annotation()
        assert "Return annotation of `reference_component` wrapped function can only be" in str(e.value)

    def test_reference_component_sample_pipeline(
        self, train_model_reference, score_data_reference, eval_model_reference
    ):
        @dsl.pipeline()
        def pipeline_with_components_from_yaml(
            training_input,
            test_input,
            training_max_epochs=20,
            training_learning_rate=1.8,
            learning_rate_schedule="time-based",
        ):
            """E2E dummy train-score-eval pipeline with components defined via yaml."""
            # Call component obj as function: apply given inputs & parameters to create a node in pipeline
            train_with_sample_data = train_model_reference(
                training_data=training_input,
                max_epocs=training_max_epochs,
                learning_rate=training_learning_rate,
                learning_rate_schedule=learning_rate_schedule,
            )

            score_with_sample_data = score_data_reference(
                model_input=train_with_sample_data.outputs.model_output, test_data=test_input
            )
            score_with_sample_data.outputs.score_output.mode = "upload"

            eval_with_sample_data = eval_model_reference(scoring_result=score_with_sample_data.outputs.score_output)

            # Return: pipeline outputs
            return {
                "trained_model": train_with_sample_data.outputs.model_output,
                "scored_data": score_with_sample_data.outputs.score_output,
                "evaluation_report": eval_with_sample_data.outputs.eval_output,
            }

        pipeline_job = pipeline_with_components_from_yaml(
            training_input=Input(type="uri_folder", path="./data/"),
            test_input=Input(type="uri_folder", path="./data/"),
            training_max_epochs=20,
            training_learning_rate=1.8,
            learning_rate_schedule="time-based",
        )

        rest_pipeline = pydash.omit(
            pipeline_job._to_rest_object().as_dict(),
            [
                "properties.jobs.train_with_sample_data.componentId",
                "properties.jobs.score_with_sample_data.componentId",
                "properties.jobs.eval_with_sample_data.componentId",
            ],
        )

        assert rest_pipeline["properties"]["jobs"] == {
            "eval_with_sample_data": {
                "_source": "YAML.COMPONENT",
                "computeId": None,
                "display_name": None,
                "distribution": None,
                "environment_variables": {},
                "inputs": {
                    "scoring_result": {
                        "job_input_type": "Literal",
                        "value": "${{parent.jobs.score_with_sample_data.outputs.score_output}}",
                    }
                },
                "limits": None,
                "name": "eval_with_sample_data",
                "outputs": {"eval_output": {"type": "Literal", "value": "${{parent.outputs.evaluation_report}}"}},
                "resources": None,
                "tags": {},
            },
            "score_with_sample_data": {
                "_source": "YAML.COMPONENT",
                "computeId": None,
                "display_name": None,
                "distribution": None,
                "environment_variables": {},
                "inputs": {
                    "model_input": {
                        "job_input_type": "Literal",
                        "value": "${{parent.jobs.train_with_sample_data.outputs.model_output}}",
                    },
                    "test_data": {"job_input_type": "Literal", "value": "${{parent.inputs.test_input}}"},
                },
                "limits": None,
                "name": "score_with_sample_data",
                "outputs": {
                    "score_output": {"type": "Literal", "value": "${{parent.outputs.scored_data}}", "mode": "Upload"}
                },
                "resources": None,
                "tags": {},
            },
            "train_with_sample_data": {
                "_source": "YAML.COMPONENT",
                "computeId": None,
                "display_name": None,
                "distribution": None,
                "environment_variables": {},
                "inputs": {
                    "learning_rate": {
                        "job_input_type": "Literal",
                        "value": "${{parent.inputs.training_learning_rate}}",
                    },
                    "learning_rate_schedule": {
                        "job_input_type": "Literal",
                        "value": "${{parent.inputs.learning_rate_schedule}}",
                    },
                    "max_epocs": {"job_input_type": "Literal", "value": "${{parent.inputs.training_max_epochs}}"},
                    "training_data": {"job_input_type": "Literal", "value": "${{parent.inputs.training_input}}"},
                },
                "limits": None,
                "name": "train_with_sample_data",
                "outputs": {"model_output": {"type": "Literal", "value": "${{parent.outputs.trained_model}}"}},
                "resources": None,
                "tags": {},
            },
        }
