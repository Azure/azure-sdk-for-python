from pathlib import Path

from azure.ai.ml import Input, MLClient, dsl, load_component
from azure.ai.ml.entities import Data, PipelineJob

parent_dir = str(Path(__file__).parent / "components")

# Load component funcs
train_model = load_component(source=parent_dir + "/train_model.yml")
score_data = load_component(source=parent_dir + "/score_data.yml")
eval_model = load_component(source=parent_dir + "/eval_model.yml")
compare2 = load_component(source=parent_dir + "/compare2.yml")


def generate_dsl_pipeline(client: MLClient) -> PipelineJob:
    try:
        input_data = client.data.get("pipeline_component_training", label="latest")
    except Exception:
        input_data = client.data.create_or_update(
            Data(name="pipeline_component_training", version="0.0.1", path=parent_dir + "/../../dataset_input/data")
        )  # type of uri_folder by default

    @dsl.pipeline()
    def train_pipeline_component(
        training_input: Input,
        test_input: Input,
        training_learning_rate: float,
        training_max_epochs: int = 20,
        learning_rate_schedule: str = "time-based",
    ):
        """E2E dummy train-score-eval pipeline with components defined via yaml."""
        # Call component obj as function: apply given inputs & parameters to create a node in pipeline
        train_with_sample_data = train_model(
            training_data=training_input,
            max_epochs=training_max_epochs,
            learning_rate=training_learning_rate,
            learning_rate_schedule=learning_rate_schedule,
        )

        score_with_sample_data = score_data(
            model_input=train_with_sample_data.outputs.model_output, test_data=test_input
        )
        score_with_sample_data.outputs.score_output.mode = "upload"

        eval_with_sample_data = eval_model(scoring_result=score_with_sample_data.outputs.score_output)

        # Return: pipeline outputs
        return {
            "trained_model": train_with_sample_data.outputs.model_output,
            "evaluation_report": eval_with_sample_data.outputs.eval_output,
        }

    # Construct pipeline
    @dsl.pipeline()
    def pipeline_with_pipeline_component(
        test_input,
        training_learning_rate1=0.1,
        training_learning_rate2=0.01,
    ):
        # Create two training pipeline component with different learning rate
        train_and_evaludate_model1 = train_pipeline_component(
            training_input=input_data, test_input=test_input, training_learning_rate=training_learning_rate1
        )
        train_and_evaludate_model2 = train_pipeline_component(
            training_input=input_data, test_input=test_input, training_learning_rate=training_learning_rate2
        )

        compare2_models = compare2(
            model1=train_and_evaludate_model1.outputs.trained_model,
            eval_result1=train_and_evaludate_model1.outputs.evaluation_report,
            model2=train_and_evaludate_model2.outputs.trained_model,
            eval_result2=train_and_evaludate_model2.outputs.evaluation_report,
        )

        # Return: pipeline outputs
        return {
            "best_model": compare2_models.outputs.best_model,
            "best_result": compare2_models.outputs.best_result,
        }

    pipeline_job = pipeline_with_pipeline_component(
        test_input=input_data,
    )

    # set pipeline level compute
    pipeline_job.settings.default_compute = "cpu-cluster"
    return pipeline_job
