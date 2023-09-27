import pytest

from azure.ai.ml import UserIdentityConfiguration
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities import CommandJob, CommandJobLimits, Job
from azure.ai.ml.entities._assets import Code
from azure.ai.ml.entities._builders.command_func import command
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.distribution import MpiDistribution, PyTorchDistribution, TensorFlowDistribution
from azure.ai.ml.entities._job.job_resource_configuration import JobResourceConfiguration
from azure.ai.ml.entities._job.sweep.early_termination_policy import TruncationSelectionPolicy
from azure.ai.ml.entities._job.sweep.objective import Objective
from azure.ai.ml.entities._job.sweep.search_space import LogUniform
from azure.ai.ml.sweep import (
    BayesianSamplingAlgorithm,
    Choice,
    GridSamplingAlgorithm,
    RandomSamplingAlgorithm,
    SweepJob,
    SweepJobLimits,
)


@pytest.mark.unittest
@pytest.mark.training_experiences_test
class TestSweepJob:
    def test_sweep_job_top_level_properties(self):
        command_job = CommandJob(
            code="./src",
            command="python train.py --ss {search_space.ss}",
            # Is it expected that using dicts do not work?
            # inputs={"input1": {"path": "trial.csv", "type": "uri_file", "mode": "rw_mount"}},
            # outputs={"default": {"mode": "rw_mount"}},
            inputs={"input1": Input(path="trial.csv")},
            outputs={"default": Output(path="./foo")},
            compute="trial",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            limits=CommandJobLimits(timeout=120),
        )
        sweep = SweepJob(
            sampling_algorithm="random",
            trial=command_job,
            search_space={"ss": Choice(type="choice", values=[{"space1": True}, {"space2": True}])},
            inputs={"input1": {"path": "top_level.csv", "type": "uri_file", "mode": "ro_mount"}},
            compute="top_level",
            limits=SweepJobLimits(trial_timeout=600),
            identity=UserIdentityConfiguration(),
        )
        rest = sweep._to_rest_object()
        sweep_job: SweepJob = Job._from_rest_object(rest)

        assert sweep_job.compute == sweep.compute
        assert sweep_job.limits.trial_timeout == sweep.limits.trial_timeout
        assert sweep_job.inputs == sweep.inputs
        assert sweep_job.outputs == sweep.outputs
        assert sweep_job.identity == sweep.identity

    def test_sweep_job_override_missing_properties(self):
        command_job = CommandJob(
            code="./src",
            command="python train.py --ss {search_space.ss}",
            # Is it expected that using dicts do not work?
            # inputs={"input1": {"path": "trial.csv", "type": "uri_file", "mode": "rw_mount"}},
            # outputs={"default": {"mode": "rw_mount"}},
            inputs={"input1": Input(path="trial.csv")},
            outputs={"default": Output(path="./foo")},
            compute="trial",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            limits=CommandJobLimits(timeout=120),
        )
        sweep = SweepJob(
            sampling_algorithm="random",
            trial=command_job,
            search_space={"ss": Choice(type="choice", values=[{"space1": True}, {"space2": True}])},
            inputs=None,
        )
        rest = sweep._to_rest_object()
        sweep_job: SweepJob = Job._from_rest_object(rest)

        assert sweep_job.compute == command_job.compute
        assert sweep_job.limits.trial_timeout == command_job.limits.timeout
        assert sweep_job.inputs == command_job.inputs
        assert sweep_job.outputs == command_job.outputs

    @pytest.mark.parametrize(
        "sampling_algorithm, expected_rest_type",
        [
            ("random", "Random"),
            ("grid", "Grid"),
            ("bayesian", "Bayesian"),
            (RandomSamplingAlgorithm(), "Random"),
            (GridSamplingAlgorithm(), "Grid"),
            (BayesianSamplingAlgorithm(), "Bayesian"),
        ],
    )
    def test_sampling_algorithm_to_rest(self, sampling_algorithm, expected_rest_type):
        command_job = CommandJob(
            code=Code(base_path="./src"),
            command="python train.py --ss {search_space.ss}",
            inputs={"input1": {"file": "trial.csv", "mode": "ro_mount"}},
            outputs={"default": {"mode": "rw_mount"}},
            compute="trial",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            limits=CommandJobLimits(timeout=120),
        )

        sweep = SweepJob(
            sampling_algorithm=sampling_algorithm,
            trial=command_job,
            search_space={"ss": Choice(type="choice", values=[{"space1": True}, {"space2": True}])},
            inputs={"input1": {"file": "top_level.csv", "mode": "ro_mount"}},
            compute="top_level",
            limits=SweepJobLimits(trial_timeout=600),
        )

        rest = sweep._to_rest_object()
        assert rest.properties.sampling_algorithm.sampling_algorithm_type == expected_rest_type

    @pytest.mark.parametrize(
        "sampling_algorithm, expected_from_rest_type",
        [
            ("random", "random"),
            ("grid", "grid"),
            ("bayesian", "bayesian"),
            (RandomSamplingAlgorithm(), "random"),
            (GridSamplingAlgorithm(), "grid"),
            (BayesianSamplingAlgorithm(), "bayesian"),
        ],
    )
    def test_sampling_algorithm_from_rest(self, sampling_algorithm, expected_from_rest_type):
        command_job = CommandJob(
            code=Code(base_path="./src"),
            command="python train.py --ss {search_space.ss}",
            inputs={"input1": Input(path="trial.csv")},
            outputs={"default": Output(path="./foo")},
            compute="trial",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            limits=CommandJobLimits(timeout=120),
        )

        sweep = SweepJob(
            sampling_algorithm=sampling_algorithm,
            trial=command_job,
            search_space={"ss": Choice(type="choice", values=[{"space1": True}, {"space2": True}])},
            inputs={"input1": Input(path="trial.csv")},
            compute="top_level",
            limits=SweepJobLimits(trial_timeout=600),
        )

        rest = sweep._to_rest_object()
        sweep: SweepJob = Job._from_rest_object(rest)
        assert sweep.sampling_algorithm.type == expected_from_rest_type

    @pytest.mark.parametrize(
        "properties_dict",
        [{}, {"seed": 999}, {"rule": "sobol"}, {"logbase": "e"}, {"seed": 999, "rule": "sobol", "logbase": "e"}],
    )
    def test_random_sampling_object_with_props(self, properties_dict):
        command_job = CommandJob(
            code=Code(base_path="./src"),
            command="python train.py --ss {search_space.ss}",
            inputs={"input1": Input(path="trial.csv")},
            outputs={"default": Output(path="./foo")},
            compute="trial",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            limits=CommandJobLimits(timeout=120),
        )

        expected_seed = properties_dict.get("seed", None)
        expected_rule = properties_dict.get("rule", None)
        expected_logbase = properties_dict.get("logbase", None)

        random_sampling_algorithm = RandomSamplingAlgorithm(**properties_dict)
        sweep = SweepJob(
            sampling_algorithm=random_sampling_algorithm,
            trial=command_job,
            search_space={"ss": Choice(type="choice", values=[{"space1": True}, {"space2": True}])},
            inputs={"input1": Input(path="trial.csv")},
            compute="top_level",
            limits=SweepJobLimits(trial_timeout=600),
        )

        rest = sweep._to_rest_object()
        assert rest.properties.sampling_algorithm.sampling_algorithm_type == "Random"
        assert rest.properties.sampling_algorithm.seed == expected_seed
        assert rest.properties.sampling_algorithm.rule == expected_rule
        assert rest.properties.sampling_algorithm.logbase == expected_logbase

        sweep: SweepJob = Job._from_rest_object(rest)
        assert sweep.sampling_algorithm.type == "random"
        assert sweep.sampling_algorithm.seed == expected_seed
        assert sweep.sampling_algorithm.rule == expected_rule
        assert sweep.sampling_algorithm.logbase == expected_logbase

    def test_sweep_job_builder_serialization(self) -> None:
        inputs = {
            "uri": Input(
                type=AssetTypes.URI_FILE, path="azureml://datastores/workspaceblobstore/paths/python/data.csv"
            ),
            "lr": LogUniform(min_value=0.001, max_value=0.1),
        }

        node = command(
            description="description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            inputs=inputs,
            command="echo ${{inputs.uri}} ${{inputs.lr}} ${{inputs.lr2}}",
            display_name="builder-sweep-job-display",
            compute="testCompute",
            experiment_name="mfe-test1-dataset",
            identity=UserIdentityConfiguration(),
            tags={"tag1": "value1"},
            properties={"prop1": "value1"},
            distribution=MpiDistribution(),
            environment_variables={"EVN1": "VAR1"},
            outputs={"best_model": {}},
            instance_count=2,
            instance_type="STANDARD_BLA",
            timeout=300,
            code="./",
        )

        sweep_node = node.sweep(
            sampling_algorithm="random",
            goal="maximize",
            primary_metric="accuracy",
            compute="sweep-compute",
            max_concurrent_trials=10,
            max_total_trials=100,
            timeout=300,
            trial_timeout=60,
            early_termination_policy=TruncationSelectionPolicy(
                evaluation_interval=100, delay_evaluation=200, truncation_percentage=40
            ),
            search_space={"lr2": LogUniform(min_value=1, max_value=100)},
        )

        # Check that the command property in the original node is kept unchanged.
        assert node.command == "echo ${{inputs.uri}} ${{inputs.lr}} ${{inputs.lr2}}"

        # job name is set in job_operations.py
        assert sweep_node.name is None
        sweep_node.name = "builder-sweep-job"

        trial = CommandJob(
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            command="echo ${{inputs.uri}} ${{search_space.lr}} ${{search_space.lr2}}",
            distribution=MpiDistribution(),
            environment_variables={"EVN1": "VAR1"},
            resources=JobResourceConfiguration(instance_count=2, instance_type="STANDARD_BLA"),
            code="./",
        )

        expected_job = SweepJob(
            trial=trial,
            name="builder-sweep-job",
            description="description",
            display_name="builder-sweep-job-display",
            compute="sweep-compute",
            experiment_name="mfe-test1-dataset",
            identity=UserIdentityConfiguration(),
            tags={"tag1": "value1"},
            properties={"prop1": "value1"},
            objective=Objective(goal="maximize", primary_metric="accuracy"),
            limits=SweepJobLimits(max_concurrent_trials=10, max_total_trials=100, timeout=300, trial_timeout=60),
            sampling_algorithm="random",
            early_termination=TruncationSelectionPolicy(
                evaluation_interval=100, delay_evaluation=200, truncation_percentage=40
            ),
            inputs={
                "uri": Input(
                    type=AssetTypes.URI_FILE, path="azureml://datastores/workspaceblobstore/paths/python/data.csv"
                )
            },
            outputs={"best_model": {}},
            search_space={
                "lr": LogUniform(min_value=0.001, max_value=0.1),
                "lr2": LogUniform(min_value=1, max_value=100),
            },
        )

        assert expected_job._to_dict() == sweep_node._to_job()._to_dict()

    @pytest.mark.parametrize(
        "distribution",
        [
            None,
            MpiDistribution(process_count_per_instance=2),
            PyTorchDistribution(process_count_per_instance=4),
            TensorFlowDistribution(parameter_server_count=2, worker_count=10),
        ],
    )
    def test_sweep_job_trial_distribution_to_rest(self, distribution) -> None:
        command_job = CommandJob(
            code="./src",
            command="python train.py --ss {search_space.ss}",
            distribution=distribution,
            inputs={"input1": Input(path="trial.csv")},
            outputs={"default": Output(path="./foo")},
            compute="trial",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            limits=CommandJobLimits(timeout=120),
        )

        sweep = SweepJob(
            sampling_algorithm="random",
            trial=command_job,
            search_space={"ss": Choice(type="choice", values=[{"space1": True}, {"space2": True}])},
            inputs={"input1": {"path": "top_level.csv", "type": "uri_file", "mode": "ro_mount"}},
            compute="top_level",
            limits=SweepJobLimits(trial_timeout=600),
            identity=UserIdentityConfiguration(),
        )

        rest_obj = sweep._to_rest_object()
        rest_obj.properties.trial.distribution == distribution._to_rest_object() if distribution else None

        # validate from rest scenario
        sweep_job: SweepJob = Job._from_rest_object(rest_obj)
        assert sweep_job.trial.distribution == sweep.trial.distribution
        assert sweep_job.compute == sweep.compute
        assert sweep_job.limits == sweep.limits
        assert sweep_job.inputs == sweep.inputs
        assert sweep_job.outputs == sweep.outputs
        assert sweep_job.identity == sweep.identity
