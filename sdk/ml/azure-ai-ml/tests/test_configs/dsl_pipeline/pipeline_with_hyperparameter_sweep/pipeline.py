from azure.ai.ml import dsl, Input
from .mldesigner_component import train_component_func, eval_component_func, score_component_func
from azure.ai.ml.sweep import (
    BanditPolicy,
    Choice,
    Randint,
    QUniform,
    QLogNormal,
    QLogUniform,
    QNormal,
    LogNormal,
    LogUniform,
    Normal,
    Uniform,
)


def generate_dsl_pipeline_with_sweep_node():
    # define a pipeline with mldesigner component
    @dsl.pipeline(
        description="Tune hyperparameters using sample components",
        default_compute="cpu-cluster",
        experiment_name="pipeline_samples",
    )
    def pipeline_with_hyperparameter_sweep(input_data, test_data):
        train_model = train_component_func(
            training_data=input_data,
            random_seed=1,
            batch_size=Choice([25, 35]),
            first_layer_neurons=Randint(upper=50),
            second_layer_neurons=QUniform(min_value=10, max_value=50, q=5),
            third_layer_neurons=QLogNormal(mu=5, sigma=1, q=5),
            epochs=QLogUniform(min_value=1, max_value=5, q=5),
            momentum=QNormal(mu=10, sigma=5, q=2),
            weight_decay=LogNormal(mu=0, sigma=1),
            learning_rate=LogUniform(min_value=-6, max_value=-1),
            f1=Normal(mu=0, sigma=1),
            f2=Uniform(min_value=10, max_value=20),
        )
        sweep_for_train = train_model.sweep(
            primary_metric="accuracy",
            goal="maximize",
            sampling_algorithm="random",
        )
        sweep_for_train.set_limits(max_total_trials=4, max_concurrent_trials=2, timeout=600)
        sweep_for_train.early_termination = BanditPolicy(evaluation_interval=2, slack_factor=0.1, delay_evaluation=1)

        score_data = score_component_func(model_input=sweep_for_train.outputs.model_output, test_data=test_data)

        eval_model = eval_component_func(scoring_result=score_data.outputs.score_output)
        return {
            "best_model_eval_output": eval_model.outputs.eval_output,
            "best_model_output": sweep_for_train.outputs.model_output,
        }

    dsl_pipeline = pipeline_with_hyperparameter_sweep(
        input_data=Input(path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
        test_data=Input(path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
    )
    return dsl_pipeline
