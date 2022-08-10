from azure.ai.ml import dsl, Input, Output, load_component
from azure.ai.ml.entities import PipelineJob
from pathlib import Path

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    # 1. Load component funcs
    prep_func = load_component(path=parent_dir + "/prep.yml")
    transform_func = load_component(path=parent_dir + "/transform.yml")
    train_func = load_component(path=parent_dir + "/train.yml")
    predict_func = load_component(path=parent_dir + "/predict.yml")
    score_func = load_component(path=parent_dir + "/score.yml")

    # 2. Construct pipeline
    @dsl.pipeline(compute="cpu-cluster", default_datastore="workspaceblobstore")
    def nyc_taxi_data_regression(pipeline_job_input):
        prep_job = prep_func(raw_data=pipeline_job_input)
        transform_job = transform_func(clean_data=prep_job.outputs.prep_data)
        train_job = train_func(training_data=transform_job.outputs.transformed_data)
        predict_job = predict_func(model_input=train_job.outputs.model_output, test_data=train_job.outputs.test_data)
        score_job = score_func(predictions=predict_job.outputs.predictions, model=train_job.outputs.model_output)
        return {
            "pipeline_job_prepped_data": prep_job.outputs.prep_data,
            "pipeline_job_transformed_data": transform_job.outputs.transformed_data,
            "pipeline_job_trained_model": train_job.outputs.model_output,
            "pipeline_job_test_data": train_job.outputs.test_data,
            "pipeline_job_predictions": predict_job.outputs.predictions,
            "pipeline_job_score_report": score_job.outputs.score_report,
        }

    pipeline = nyc_taxi_data_regression(Input(path=parent_dir + "/data/"))
    pipeline.outputs.pipeline_job_prepped_data = Output(path="/prepped_data", mode="rw_mount")
    pipeline.outputs.pipeline_job_transformed_data = Output(path="/transformed_data", mode="rw_mount")
    pipeline.outputs.pipeline_job_trained_model = Output(path="/trained-model", mode="rw_mount")
    pipeline.outputs.pipeline_job_test_data = Output(path="/test_data", mode="rw_mount")
    pipeline.outputs.pipeline_job_predictions = Output(path="/predictions", mode="rw_mount")
    pipeline.outputs.pipeline_job_score_report = Output(path="/report", mode="rw_mount")
    return pipeline
