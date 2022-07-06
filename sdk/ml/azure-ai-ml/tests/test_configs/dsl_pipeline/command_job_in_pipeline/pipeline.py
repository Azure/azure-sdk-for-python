from azure.ai.ml import dsl, command, Input
from azure.ai.ml.entities import PipelineJob
from pathlib import Path

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    environment = "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5"

    # 1. Construct command job
    train_func = command(
        inputs=dict(
            training_data=Input(path=parent_dir + "/data/"),
            max_epocs=20,
            learning_rate=1.8,
            learning_rate_schedule='time-based',
        ),
        outputs=dict(
            model_output=None
        ),
        display_name="my-train-job",
        code=parent_dir + "/train_src",
        environment=environment,
        command="python train.py --training_data ${{inputs.training_data}} --max_epocs ${{inputs.max_epocs}} "
                "--learning_rate ${{inputs.learning_rate}} --learning_rate_schedule "
                "${{inputs.learning_rate_schedule}} --model_output ${{outputs.model_output}}"
    )

    score_func = command(
        inputs=dict(
            model_input=Input(path=parent_dir + "/data/"),
            test_data=Input(path=parent_dir + "/data/"),
        ),
        outputs=dict(
            score_output=None
        ),
        display_name="my-score-job",
        code=parent_dir + "/train_src",
        environment=environment,
        command="python score.py --model_input ${{inputs.model_input}} "
                "--test_data ${{inputs.test_data}} --score_output ${{outputs.score_output}}"
    )

    eval_func = command(
        inputs=dict(
            scoring_result=Input(path=parent_dir + "/data/"),
        ),
        outputs=dict(
            eval_output=None
        ),
        display_name="my-evaluate-job",
        environment=environment,
        command='echo "hello world"'
    )

    # 2. Construct pipeline
    @dsl.pipeline(
        compute="cpu-cluster",
    )
    def command_job_in_pipeline(
            pipeline_job_training_input,
            pipeline_job_test_input,
            pipeline_job_training_max_epocs,
            pipeline_job_training_learning_rate,
            pipeline_job_learning_rate_schedule,
    ):
        # TODO: the target of this test changed as Input binding is not supported now?
        train_job = train_func(
            training_data=Input(path=parent_dir + "/data/"),
            max_epocs=20,
            learning_rate=1.8,
            learning_rate_schedule='time-based',
        )

        score_job = score_func(
            model_input=train_job.outputs.model_output,
            test_data=pipeline_job_test_input,
        )
        score_job.compute = "gpu-cluster"

        evaluate_job = eval_func(scoring_result=Input(path=parent_dir + "/data/"))
        evaluate_job.compute = "cpu-cluster"
        # return {
        #     "pipeline_job_trained_model": train_job.outputs.model_output,
        #     "pipeline_job_scored_data": score_job.outputs.score_output,
        #     "pipeline_job_evaluation_report": evaluate_job.outputs.eval_output,
        # }

    pipeline = command_job_in_pipeline(
        Input(path=parent_dir + "/data/"),
        Input(path=parent_dir + "/data/"),
        20,
        1.8,
        "time-based",
    )

    return pipeline
