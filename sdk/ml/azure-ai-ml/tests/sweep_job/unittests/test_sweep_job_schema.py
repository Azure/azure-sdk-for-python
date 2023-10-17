import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from azure.ai.ml import load_job
from azure.ai.ml._restclient.v2023_04_01_preview.models import AmlToken as RestAmlToken
from azure.ai.ml._restclient.v2023_04_01_preview.models import InputDeliveryMode, JobInputType, JobOutputType
from azure.ai.ml._restclient.v2023_04_01_preview.models import ManagedIdentity as RestManagedIdentity
from azure.ai.ml._restclient.v2023_04_01_preview.models import OutputDeliveryMode
from azure.ai.ml._restclient.v2023_04_01_preview.models import UriFolderJobOutput as RestUriFolderJobOutput
from azure.ai.ml._restclient.v2023_04_01_preview.models import UserIdentity as RestUserIdentity
from azure.ai.ml._schema import SweepJobSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AssetTypes, InputOutputModes
from azure.ai.ml.entities import (
    AmlTokenConfiguration,
    CommandJob,
    Job,
    ManagedIdentityConfiguration,
    UserIdentityConfiguration,
)
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.sweep.search_space import SweepDistribution
from azure.ai.ml.entities._job.to_rest_functions import to_rest_job_object
from azure.ai.ml.sweep import (
    Choice,
    LogNormal,
    LogUniform,
    Normal,
    QLogNormal,
    QLogUniform,
    QNormal,
    QUniform,
    Randint,
    SamplingAlgorithm,
    SweepJob,
    Uniform,
)


@pytest.mark.unittest
@pytest.mark.training_experiences_test
class TestSweepJobSchema:
    @pytest.mark.parametrize(
        "search_space, expected",
        [
            (Choice([1.0, 2.0, 3.0]), ["choice", [[1.0, 2.0, 3.0]]]),
            (Normal(1.0, 2.0), ["normal", [1.0, 2.0]]),
            (QNormal(1.0, 2.0, 3), ["qnormal", [1.0, 2.0, 3]]),
            (LogNormal(1.0, 2.0), ["lognormal", [1.0, 2.0]]),
            (QLogNormal(1.0, 2.0, 3), ["qlognormal", [1.0, 2.0, 3]]),
            (Randint(3), ["randint", [3]]),
            (Uniform(1.0, 10.0), ["uniform", [1.0, 10.0]]),
            (QUniform(1.0, 10.0, 3), ["quniform", [1.0, 10.0, 3]]),
            (LogUniform(1.0, 10.0), ["loguniform", [1.0, 10.0]]),
            (QLogUniform(1.0, 10.0, 3), ["qloguniform", [1.0, 10.0, 3]]),
        ],
    )
    def test_search_space_to_rest(self, search_space: SweepDistribution, expected):
        command_job = CommandJob(
            code="./src",
            command="python train.py --lr 0.01",
            inputs={"input1": Input(path="testdata:1")},
            compute="local",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        )

        sweep = SweepJob(sampling_algorithm="random", trial=command_job, search_space={"ss": search_space})
        rest = sweep._to_rest_object()

        assert rest.properties.search_space == {"ss": expected}

    @pytest.mark.parametrize(
        "expected, rest_search_space",
        [
            (Choice([1.0, 2.0, 3.0]), ["choice", [[1.0, 2.0, 3.0]]]),
            (Normal(1.0, 2.0), ["normal", [1.0, 2.0]]),
            (QNormal(1.0, 2.0, 3), ["qnormal", [1.0, 2.0, 3]]),
            (LogNormal(1.0, 2.0), ["lognormal", [1.0, 2.0]]),
            (QLogNormal(1.0, 2.0, 3), ["qlognormal", [1.0, 2.0, 3]]),
            (Randint(3), ["randint", [3]]),
            (Uniform(1.0, 10.0), ["uniform", [1.0, 10.0]]),
            (QUniform(1.0, 10.0, 3), ["quniform", [1.0, 10.0, 3]]),
            (LogUniform(1.0, 10.0), ["loguniform", [1.0, 10.0]]),
            (QLogUniform(1.0, 10.0, 3), ["qloguniform", [1.0, 10.0, 3]]),
        ],
    )
    def test_search_space_from_rest(self, expected: SweepDistribution, rest_search_space):
        command_job = CommandJob(
            code="./src",
            command="python train.py --ss {search_space.ss}",
            inputs={"input1": Input(path="testdata:1")},
            compute="local",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        )
        sweep = SweepJob(sampling_algorithm="random", trial=command_job, search_space={"ss": Choice([1.0, 2.0, 3.0])})

        rest = sweep._to_rest_object()
        rest.properties.search_space = {"ss": rest_search_space}
        sweep: SweepJob = Job._from_rest_object(rest)
        assert sweep.search_space == {"ss": expected}

    def test_sweep_with_ints(self):
        expected_rest = ["quniform", [1, 100, 1]]
        expected_ss = {"type": "quniform", "min_value": 1, "max_value": 100, "q": 1}

        command_job = CommandJob(
            code="./src",
            command="python train.py --ss {search_space.ss}",
            inputs={"input1": Input(path="testdata:1")},
            compute="local",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        )
        sweep = SweepJob(
            sampling_algorithm="random",
            trial=command_job,
            search_space={"ss": QUniform(type="quniform", min_value=1, max_value=100, q=1)},
        )
        rest = sweep._to_rest_object()
        sweep: SweepJob = Job._from_rest_object(rest)

        assert rest.properties.search_space["ss"] == expected_rest
        assert vars(sweep.search_space["ss"]) == expected_ss
        for var in rest.properties.search_space["ss"][1]:
            assert type(var) == int

    def test_sweep_with_floats(self):
        expected_rest = ["quniform", [1.1, 100.12, 1]]
        expected_ss = {"type": "quniform", "min_value": 1.1, "max_value": 100.12, "q": 1}

        command_job = CommandJob(
            code="./src",
            command="python train.py --ss {search_space.ss}",
            inputs={"input1": Input(path="testdata:1")},
            compute="local",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        )
        sweep = SweepJob(
            sampling_algorithm="random",
            trial=command_job,
            search_space={"ss": QUniform(type="quniform", min_value=1.1, max_value=100.12, q=1)},
        )
        rest = sweep._to_rest_object()
        sweep: SweepJob = Job._from_rest_object(rest)

        assert rest.properties.search_space["ss"] == expected_rest
        assert vars(sweep.search_space["ss"]) == expected_ss
        # Ensure that min_value and max_value are floats, ignoring q
        for var in rest.properties.search_space["ss"][1][:2]:
            assert type(var) == float

    def test_sweep_with_string(self):
        expected_rest = ["choice", [["gbdt", "dart"]]]
        expected_ss = {"type": "choice", "values": ["gbdt", "dart"]}
        command_job = CommandJob(
            code="./src",
            command="python train.py --ss {search_space.ss}",
            inputs={"input1": Input(path="testdata:1")},
            compute="local",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        )
        sweep = SweepJob(
            sampling_algorithm="random",
            trial=command_job,
            search_space={"ss": Choice(type="choice", values=["gbdt", "dart"])},
        )
        rest = sweep._to_rest_object()
        sweep: SweepJob = Job._from_rest_object(rest)

        assert rest.properties.search_space["ss"] == expected_rest
        assert vars(sweep.search_space["ss"]) == expected_ss

    def test_inputs_types_sweep_job(self):
        original_entity = load_job(Path("./tests/test_configs/sweep_job/sweep_job_input_types.yml"))
        rest_representation = to_rest_job_object(original_entity)
        reconstructed_entity = Job._from_rest_object(rest_representation)

        assert original_entity.inputs["test_dataset"].mode is None
        assert rest_representation.properties.inputs["test_dataset"].job_input_type == JobInputType.URI_FOLDER
        assert rest_representation.properties.inputs["test_dataset"].mode is None
        assert reconstructed_entity.inputs["test_dataset"].mode is None

        assert original_entity.inputs["test_url"].mode == InputOutputModes.RO_MOUNT
        assert original_entity.inputs["test_url"].type == AssetTypes.URI_FILE
        assert original_entity.inputs["test_url"].path == "azureml://fake/url.json"
        assert rest_representation.properties.inputs["test_url"].job_input_type == JobInputType.URI_FILE
        assert rest_representation.properties.inputs["test_url"].mode == InputDeliveryMode.READ_ONLY_MOUNT
        assert rest_representation.properties.inputs["test_url"].uri == "azureml://fake/url.json"
        assert reconstructed_entity.inputs["test_url"].mode == InputOutputModes.RO_MOUNT
        assert reconstructed_entity.inputs["test_url"].type == AssetTypes.URI_FILE
        assert reconstructed_entity.inputs["test_url"].path == "azureml://fake/url.json"

        assert original_entity.inputs["test_string_literal"] == "literal string"
        assert rest_representation.properties.inputs["test_string_literal"].job_input_type == JobInputType.LITERAL
        assert rest_representation.properties.inputs["test_string_literal"].value == "literal string"
        assert reconstructed_entity.inputs["test_string_literal"] == "literal string"

        assert original_entity.inputs["test_literal_valued_int"] == 42
        assert rest_representation.properties.inputs["test_literal_valued_int"].job_input_type == JobInputType.LITERAL
        assert rest_representation.properties.inputs["test_literal_valued_int"].value == "42"
        assert reconstructed_entity.inputs["test_literal_valued_int"] == "42"

    def test_outputs_types_standalone_jobs(self):
        original_entity = load_job(Path("./tests/test_configs/sweep_job/sweep_job_output_types.yml"))
        rest_representation = to_rest_job_object(original_entity)
        dummy_default = RestUriFolderJobOutput(uri="azureml://foo", mode=OutputDeliveryMode.READ_WRITE_MOUNT)
        rest_representation.properties.outputs["default"] = dummy_default
        reconstructed_entity = Job._from_rest_object(rest_representation)

        assert original_entity.outputs["test1"] is None
        assert rest_representation.properties.outputs["test1"].job_output_type == JobOutputType.URI_FOLDER
        assert rest_representation.properties.outputs["test1"].mode is None

        assert original_entity.outputs["test2"].mode == InputOutputModes.UPLOAD
        assert rest_representation.properties.outputs["test2"].job_output_type == JobOutputType.URI_FOLDER
        assert rest_representation.properties.outputs["test2"].mode == OutputDeliveryMode.UPLOAD

        assert original_entity.outputs["test3"].mode == InputOutputModes.RW_MOUNT
        assert rest_representation.properties.outputs["test3"].job_output_type == JobOutputType.URI_FOLDER
        assert rest_representation.properties.outputs["test3"].mode == OutputDeliveryMode.READ_WRITE_MOUNT
        assert reconstructed_entity.outputs["default"].path == "azureml://foo"

    def test_sweep_with_dicts(self):
        expected_rest = ["choice", [[{"space1": True}, {"space2": True}]]]
        expected_ss = {"type": "choice", "values": [{"space1": True}, {"space2": True}]}

        command_job = CommandJob(
            code="./src",
            command="python train.py --ss {search_space.ss}",
            inputs={"input1": Input(path="testdata:1")},
            compute="local",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        )
        sweep = SweepJob(
            sampling_algorithm="random",
            trial=command_job,
            search_space={"ss": Choice(type="choice", values=[{"space1": True}, {"space2": True}])},
        )
        rest = sweep._to_rest_object()
        sweep: SweepJob = Job._from_rest_object(rest)
        assert rest.properties.search_space["ss"] == expected_rest
        assert vars(sweep.search_space["ss"]) == expected_ss
        # Ensure that all elements of values are dicts
        for var in rest.properties.search_space["ss"][1][0]:
            assert type(var) == dict

    def test_sweep_termination_roundtrip(self):
        paths = [
            "./tests/test_configs/sweep_job/sweep-median.yaml",
            "./tests/test_configs/sweep_job/sweep-bandit.yaml",
            "./tests/test_configs/sweep_job/sweep-truncation.yaml",
            "./tests/test_configs/sweep_job/sweep_job_search_space_choice_string.yml",
        ]
        context = {BASE_PATH_CONTEXT_KEY: Path(paths[0]).parent}
        schema = SweepJobSchema(context=context)
        cfg = None

        for path in paths:
            with open(path, "r") as f:
                cfg = yaml.safe_load(f)
            internal_representation: SweepJob = Job._load(data=cfg)
            rest_intermediate = internal_representation._to_rest_object()
            internal_obj = SweepJob._from_rest_object(rest_intermediate)
            reconstructed_yaml = schema.dump(internal_obj)
            assert reconstructed_yaml["early_termination"]["type"] == cfg["early_termination"]["type"]

    def test_sweep_search_space_environment_variables(self):
        sweep: SweepJob = load_job(Path("./tests/test_configs/sweep_job/sweep-search.yaml"))
        # This is to guard against using mutable values as default for constructor args
        assert sweep.search_space["dropout_rate"] != sweep.search_space["dropout_rate2"]

        rest_intermediate = sweep._to_rest_object()
        rest_command = rest_intermediate.properties.trial.command
        for param in sweep.search_space.keys():
            assert f"--{param} ${{{{search_space.{param}}}}}" in rest_command

    def test_sweep_job_recursive_search_space(self):
        yaml_path = Path("./tests/test_configs/sweep_job/sweep_job_recursive_search_space.yaml")
        with open(yaml_path, "r") as f:
            yaml_job = yaml.safe_load(f)
        job: SweepJob = load_job(Path("./tests/test_configs/sweep_job/sweep_job_recursive_search_space.yaml"))
        rest_job = job._to_rest_object()

        with open("./tests/test_configs/sweep_job/expected_recursive_search_space.json") as f:
            expected_recursive_search_space = json.load(f)
        assert rest_job.properties.search_space == expected_recursive_search_space

        from_rest_sweep_job = Job._from_rest_object(rest_job)
        assert json.loads(json.dumps(from_rest_sweep_job._to_dict()))["search_space"] == json.loads(
            json.dumps(yaml_job["search_space"])
        )

    @pytest.mark.parametrize(
        "yaml_path,expected_sampling_algorithm",
        [
            ("./tests/test_configs/sweep_job/sweep_job_minimal_test.yaml", "random"),
            (
                "./tests/test_configs/sweep_job/string_sampling_algorithm/sweep_job_grid_sampling_algorithm_string.yml",
                "grid",
            ),
            (
                "./tests/test_configs/sweep_job/string_sampling_algorithm/sweep_job_bayesian_sampling_algorithm_string.yml",
                "bayesian",
            ),
        ],
    )
    def test_sampling_algorithm_string_preservation(self, yaml_path: str, expected_sampling_algorithm: str):
        sweep_entity: SweepJob = load_job(Path(yaml_path))
        assert isinstance(sweep_entity.sampling_algorithm, str)
        assert sweep_entity.sampling_algorithm == expected_sampling_algorithm

    @pytest.mark.parametrize(
        "yaml_path,expected_sampling_algorithm",
        [
            (
                "./tests/test_configs/sweep_job/object_sampling_algorithm/sweep_job_random_sampling_algorithm_object.yml",
                "random",
            ),
            (
                "./tests/test_configs/sweep_job/object_sampling_algorithm/sweep_job_grid_sampling_algorithm_object.yml",
                "grid",
            ),
            (
                "./tests/test_configs/sweep_job/object_sampling_algorithm/sweep_job_bayesian_sampling_algorithm_object.yml",
                "bayesian",
            ),
        ],
    )
    def test_sampling_algorithm_object_preservation(self, yaml_path: str, expected_sampling_algorithm: str):
        sweep_entity = load_job(Path(yaml_path))
        assert isinstance(sweep_entity.sampling_algorithm, SamplingAlgorithm)
        assert sweep_entity.sampling_algorithm.type == expected_sampling_algorithm

    @pytest.mark.parametrize(
        "yaml_path,property_name,expected_value",
        [
            ("./tests/test_configs/sweep_job/sampling_algorithm_properties/sweep_job_random_seed.yml", "seed", 999),
            ("./tests/test_configs/sweep_job/sampling_algorithm_properties/sweep_job_random_rule.yml", "rule", "sobol"),
            (
                "./tests/test_configs/sweep_job/sampling_algorithm_properties/logbase_values/sweep_job_random_logbase_e.yml",
                "logbase",
                "e",
            ),
            (
                "./tests/test_configs/sweep_job/sampling_algorithm_properties/logbase_values/sweep_job_random_logbase_number.yml",
                "logbase",
                2,
            ),
            (
                "./tests/test_configs/sweep_job/sampling_algorithm_properties/logbase_values/sweep_job_random_logbase_float.yml",
                "logbase",
                2.5,
            ),
        ],
    )
    def test_sampling_algorithm_object_properties(self, yaml_path: str, property_name: str, expected_value: Any):
        sweep_entity = load_job(Path(yaml_path))
        assert isinstance(sweep_entity.sampling_algorithm, SamplingAlgorithm)
        assert sweep_entity.sampling_algorithm.__dict__[property_name] == expected_value

    @pytest.mark.parametrize(
        ("identity", "rest_identity"),
        [
            (AmlTokenConfiguration(), RestAmlToken()),
            (UserIdentityConfiguration(), RestUserIdentity()),
            (ManagedIdentityConfiguration(), RestManagedIdentity()),
        ],
    )
    def test_identity_to_rest(self, identity, rest_identity):
        command_job = CommandJob(
            code="./src",
            command="python train.py --lr 0.01",
            inputs={"input1": Input(path="testdata:1")},
            compute="local",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        )

        sweep = SweepJob(
            sampling_algorithm="random",
            trial=command_job,
            identity=identity,
            search_space={"ss": QUniform(type="quniform", min_value=1, max_value=100, q=1)},
        )
        rest = sweep._to_rest_object()

        assert rest.properties.identity == rest_identity
