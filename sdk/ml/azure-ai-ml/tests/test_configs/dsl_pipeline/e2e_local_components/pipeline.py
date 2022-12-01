from pathlib import Path

from azure.ai.ml import Input, dsl, load_component
from azure.ai.ml.entities import PipelineJob

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    # 1. Load component funcs
    train_func = load_component(source=parent_dir + "/train.yml")
    score_func = load_component(source=parent_dir + "/score.yml")
    eval_func = load_component(source=parent_dir + "/eval.yml")

    # 2. Construct pipeline
    @dsl.pipeline(
        compute="cpu-cluster",
        description="Dummy train-score-eval pipeline with local components",
    )
    def e2e_local_components(
        pipeline_job_training_input,
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
        train_job.compute = "cpu-cluster"
        score_job = score_func(
            model_input=train_job.outputs.model_output,
            test_data=Input(path=parent_dir + "/data/"),
        )
        score_job.outputs.score_output.mode = "upload"
        score_job.compute = "cpu-cluster"
        evaluate_job = eval_func(scoring_result=score_job.outputs.score_output)
        evaluate_job.compute = "cpu-cluster"
        return {
            "pipeline_job_trained_model": train_job.outputs.model_output,
            "pipeline_job_evaluation_report": evaluate_job.outputs.eval_output,
        }

    pipeline = e2e_local_components(
        Input(path=parent_dir + "/data/"),
        20,
        1.8,
        "time-based",
    )
    pipeline.outputs.pipeline_job_trained_model.mode = "upload"
    # pipeline.outputs.pipeline_job_evaluation_report.mode = "upload"
    return pipeline
