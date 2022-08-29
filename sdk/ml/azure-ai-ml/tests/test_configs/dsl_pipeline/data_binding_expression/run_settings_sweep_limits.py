from azure.core.exceptions import ResourceNotFoundError
from azure.ai.ml import dsl, MLClient, Input, MpiDistribution, load_component
from azure.ai.ml.entities import PipelineJob
from azure.ai.ml.entities import Data
from pathlib import Path

from azure.ai.ml.entities._job.sweep.search_space import Choice

base_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    # 1. Load component funcs
    basic_func = load_component(path=base_dir + "/../../components/helloworld_component_for_sweep.yml")
    uri_file_input = Input(type="uri_file", path="../../data/sample1.csv")
    uri_folder_input = Input(type="uri_folder", path="../../data")

    # 2. Construct pipeline
    @dsl.pipeline(
        description="The hello world pipeline job with data binding",
        compute="cpu-cluster",
        tags={"owner": "sdkteam", "tag": "tagvalue"},
    )
    def pipeline_with_data_binding(
        job_in_folder,
        job_in_file,
        job_in_number: int = 1,
        job_in_string: str = "hello",
        target_compute: str = "cpu-cluster",
        output_file_name: str = "sample1.csv",
    ):
        hello_world = basic_func(
            batch_size=Choice([25, 35]),
            data_folder=job_in_folder,
            first_layer_neurons=32,
            second_layer_neurons=32,
            third_layer_neurons=5,
            epochs=1,
            momentum=10,
            weight_decay=0.01,
            learning_rate=0.001,
            f1=0.5,
            f2=15,
            random_seed=42,
        )
        hello_world_sweep = hello_world.sweep(
            primary_metric="accuracy",
            max_total_trials=job_in_number,
            goal="maximize",
            sampling_algorithm="random",
        )

    pipeline_obj = pipeline_with_data_binding(job_in_folder=uri_folder_input, job_in_file=uri_file_input)
    return pipeline_obj
