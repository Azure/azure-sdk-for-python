import pytest
from azure.ai.ml import Input, MLClient

from azure.ai.ml.entities._builders import Command, Parallel

from mldesigner import reference_component


@pytest.fixture()
def hello_world_component_reference():
    test_path = "./tests/test_configs/components/helloworld_component.yml"

    @reference_component(path=test_path)
    def hello_world(component_in_path: Input = None, component_in_number: int = None) -> Command:
        ...

    return hello_world


@pytest.fixture
def hello_world_component_reference_remote(client: MLClient, hello_world_component):
    @reference_component(name=hello_world_component.name, version=hello_world_component.version)
    def hello_world(
        component_in_path: Input = None,
        component_in_number: int = None,
    ) -> Command:
        ...

    return hello_world


@pytest.fixture
def batch_inference_component_reference():
    test_path = "./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/score.yml"

    @reference_component(path=test_path)
    def batch_inference(job_data_path: Input = None) -> Parallel:
        ...

    return batch_inference


@pytest.fixture
def batch_inference_component_reference_remote(client: MLClient, batch_inference):
    @reference_component(name=batch_inference.name, version=batch_inference.version)
    def batch_inference_func(job_data_path: Input = None) -> Parallel:
        ...

    return batch_inference_func


@pytest.fixture
def eval_model_reference():
    test_path = "./tests/test_configs/dsl_pipeline/e2e_registered_components/eval.yml"

    @reference_component(
        path=test_path,
    )
    def eval_model(
        scoring_result: Input = None,
    ) -> Command:
        """A dummy evaluate component

        Args:
            scoring_result (Input): uri_folder (type: uri_folder)

        Returns:
            A component node.
            The component contains the following outputs:
                eval_output (Output): uri_folder (type: uri_folder)
            reference the outputs by:
                node.outputs.eval_output
        """
        ...

    return eval_model


@pytest.fixture
def score_data_reference():
    test_path = "./tests/test_configs/dsl_pipeline/e2e_registered_components/score.yml"

    @reference_component(
        path=test_path,
    )
    def score_data(
        model_input: Input = None,
        test_data: Input = None,
    ) -> Command:
        """A dummy scoring component

        Args:
            model_input (Input): uri_folder (type: uri_folder)
            test_data (Input): uri_folder (type: uri_folder)

        Returns:
            A component node.
            The component contains the following outputs:
                score_output (Output): uri_folder (type: uri_folder)
            reference the outputs by:
                node.outputs.score_output
        """
        ...

    return score_data


@pytest.fixture
def train_model_reference():
    test_path = "./tests/test_configs/dsl_pipeline/e2e_registered_components/train.yml"

    @reference_component(path=test_path)
    def train_model(
        learning_rate: float = 0.01,
        learning_rate_schedule: str = "time-based",
        max_epocs: int = None,
        training_data: Input = None,
    ) -> Command:
        """A dummy training component

        Args:
            learning_rate (float): number
            learning_rate_schedule (str): string
            max_epocs (int): integer
            training_data (Input): uri_folder (type: uri_folder)

        Returns:
            A component node.
            The component contains the following outputs:
                model_output (Output): uri_folder (type: uri_folder)
            reference the outputs by:
                node.outputs.model_output
        """
        ...

    return train_model
