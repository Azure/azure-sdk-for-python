from azure.ai.ml import dsl, MLClient, Input, load_component
from azure.ai.ml.entities import PipelineJob
from azure.ai.ml.entities import Component as ComponentEntity
from pathlib import Path

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline(
    client: MLClient,
    pipeline_samples_e2e_registered_train_components: ComponentEntity,
    pipeline_samples_e2e_registered_score_components: ComponentEntity,
    pipeline_samples_e2e_registered_eval_components: ComponentEntity,
) -> PipelineJob:
    # 1. Load component funcs
    train_func = load_component(
        client=client,
        name=pipeline_samples_e2e_registered_train_components.name,
        version=pipeline_samples_e2e_registered_train_components.version,
    )
    score_func = load_component(
        client=client,
        name=pipeline_samples_e2e_registered_score_components.name,
        version=pipeline_samples_e2e_registered_score_components.version,
    )
    eval_func = load_component(
        client=client,
        name=pipeline_samples_e2e_registered_eval_components.name,
        version=pipeline_samples_e2e_registered_eval_components.version,
    )

    # 2. Construct pipeline
    @dsl.pipeline(
        compute="cpu-cluster",
        description="E2E dummy train-score-eval pipeline with registered components",
    )
    def e2e_registered_components(
        pipeline_job_training_input,
        pipeline_job_test_input,
        pipeline_job_training_max_epocs,
        pipeline_job_training_learning_rate,
        pipeline_job_learning_rate_schedule,
    ):
        train_job = train_func(
            training_data=pipeline_job_training_input,
            max_epocs=pipeline_job_training_max_epocs,
            learning_rate=pipeline_job_training_learning_rate,
            learning_rate_schedule=pipeline_job_learning_rate_schedule,
        )
        score_job = score_func(model_input=train_job.outputs.model_output, test_data=pipeline_job_test_input)
        score_job.outputs.score_output.mode = "upload"
        evaluate_job = eval_func(scoring_result=score_job.outputs.score_output)
        return {
            "pipeline_job_trained_model": train_job.outputs.model_output,
            "pipeline_job_scored_data": score_job.outputs.score_output,
            "pipeline_job_evaluation_report": evaluate_job.outputs.eval_output,
        }

    pipeline = e2e_registered_components(
        Input(path=parent_dir + "/data/"),
        Input(path=parent_dir + "/data/"),
        20,
        1.8,
        "time-based",
    )
    pipeline.outputs.pipeline_job_trained_model.mode = "upload"
    pipeline.outputs.pipeline_job_scored_data.mode = "upload"
    pipeline.outputs.pipeline_job_evaluation_report.mode = "upload"
    return pipeline
