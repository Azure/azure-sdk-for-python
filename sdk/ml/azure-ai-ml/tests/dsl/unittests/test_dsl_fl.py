from typing import List
from pathlib import Path
import pytest
import os
from azure.ai.ml import command, Input, Output, load_component
from azure.ai.ml.entities._builders.fl_scatter_gather import FLScatterGather
from azure.ai.ml.entities._assets.federated_learning_silo import FederatedLearningSilo
from azure.ai.ml.dsl._fl_scatter_gather_node import _check_for_import
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.dsl import pipeline

from .._util import _DSL_TIMEOUT_SECOND


@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestDSLPipeline:
    def test_fl_node_creation(
        self,
        federated_learning_components_folder: Path,
        federated_learning_local_data_folder: Path,
    ) -> None:
        # To support dsl pipeline kwargs
        os.environ["AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED"] = "True"

        preprocessing_component = load_component(
            source=os.path.join(federated_learning_components_folder, "preprocessing", "spec.yaml")
        )

        training_component = load_component(
            source=os.path.join(federated_learning_components_folder, "training", "spec.yaml")
        )

        aggregate_component = load_component(
            source=os.path.join(federated_learning_components_folder, "aggregate", "spec.yaml")
        )

        aggregation_step = aggregate_component

        compute_names = [
            "siloCompute1",
            "siloCompute2",
            "siloCompute3",
            "aggCompute",
        ]
        datastore_names = [
            "silo_datastore1",
            "silo_datastore2",
            "silo_datastore3",
            "agg_datastore",
        ]

        @pipeline
        def silo_step_func(
            raw_train_data: Input,
            raw_test_data: Input,
            checkpoint: Input(optional=True),
            lr: float = 0.01,
            batch_size: int = 64,
            iteration_num: int = 0,
            epochs: int = 3,
        ):
            # Preprocess data
            silo_pre_processing_step = preprocessing_component(
                raw_training_data=raw_train_data,
                raw_testing_data=raw_test_data,
                # raw_evaluation_data=raw_eval_data,
                # here we're using the name of the silo compute as a metrics prefix
                metrics_prefix="",
            )

            # Run training
            silo_training_step = training_component(
                train_data=silo_pre_processing_step.outputs.processed_train_data,
                test_data=silo_pre_processing_step.outputs.processed_test_data,
                checkpoint=checkpoint,
                lr=lr,
                epochs=epochs,
                batch_size=batch_size,
                metrics_prefix="",
                iteration_num=iteration_num,
            )
            # return training results
            return {
                "model": silo_training_step.outputs.model,
            }

        silo_configs = [
            FederatedLearningSilo(
                compute=compute_names[0],
                datastore=datastore_names[0],
                inputs={
                    "raw_train_data": Input(
                        type=AssetTypes.URI_FILE,
                        mode="direct",
                        path=os.path.join(federated_learning_local_data_folder, "silo1_input1.txt"),
                        datastore=datastore_names[0],
                    ),
                    "raw_test_data": Input(
                        type=AssetTypes.URI_FILE,
                        mode="direct",
                        path=os.path.join(federated_learning_local_data_folder, "silo1_input2.txt"),
                        datastore=datastore_names[0],
                    ),
                },
            ),
            FederatedLearningSilo(
                compute=compute_names[1],
                datastore=datastore_names[1],
                inputs={
                    "raw_train_data": Input(
                        type=AssetTypes.URI_FILE,
                        mode="mount",
                        path=os.path.join(federated_learning_local_data_folder, "silo2_input1.txt"),
                        datastore=datastore_names[1],
                    ),
                    "raw_test_data": Input(
                        type=AssetTypes.URI_FILE,
                        mode="direct",
                        path=os.path.join(federated_learning_local_data_folder, "silo2_input2.txt"),
                        datastore=datastore_names[1],
                    ),
                },
            ),
            FederatedLearningSilo(
                compute=compute_names[2],
                datastore=datastore_names[2],
                inputs={
                    "raw_train_data": Input(
                        type=AssetTypes.URI_FILE,
                        mode="mount",
                        path=os.path.join(federated_learning_local_data_folder, "silo3_input1.txt"),
                        datastore=datastore_names[2],
                    ),
                    "raw_test_data": Input(
                        type=AssetTypes.URI_FILE,
                        mode="mount",
                        path=os.path.join(federated_learning_local_data_folder, "silo3_input2.txt"),
                        datastore=datastore_names[2],
                    ),
                },
            ),
        ]

        silo_to_aggregation_argument_map = {"model": "silo_inputs"}
        aggregation_to_silo_argument_map = {"aggregated_output": "checkpoint"}

        # Other args
        iterations = 3
        silo_kwargs = {}
        agg_kwargs = {}
        aggregation_compute = datastore_names[3]
        aggregation_datastore = datastore_names[3]

        fl_node = FLScatterGather(
            silo_configs=silo_configs,
            silo_component=silo_step_func,
            aggregation_component=aggregation_step,
            aggregation_compute=aggregation_compute,
            aggregation_datastore=aggregation_datastore,
            shared_silo_kwargs=silo_kwargs,
            aggregation_kwargs=agg_kwargs,
            silo_to_aggregation_argument_map=silo_to_aggregation_argument_map,
            aggregation_to_silo_argument_map=aggregation_to_silo_argument_map,
            max_iterations=iterations,
        )

        # Validate scatter-gather graph
        assert fl_node.scatter_gather_graph.type == "pipeline"
        scatter_gather_body = fl_node.scatter_gather_graph.component.jobs["scatter_gather_body"]
        assert scatter_gather_body

        silo_idx = 0
        for job_name, job_body in scatter_gather_body.component.jobs.items():
            if job_name in [
                "executed_merge_component",
                "executed_aggregation_component",
            ]:
                # Validate Merge and Aggregation component
                assert job_body.compute == aggregation_compute
                assert aggregation_datastore in job_body.outputs["aggregated_output"].path
            else:
                # Validate silo component

                # Preprocessing
                preprocessed_step = job_body.component.jobs["silo_pre_processing_step"]
                assert preprocessed_step.outputs["processed_train_data"]
                assert preprocessed_step.outputs["processed_test_data"]
                assert preprocessed_step.compute == silo_configs[silo_idx].compute

                # Training
                training_step = job_body.component.jobs["silo_training_step"]
                assert aggregation_datastore in training_step.outputs["model"].path
                silo_idx += 1

        # Final Output
        assert fl_node.outputs.keys() == aggregation_to_silo_argument_map.keys()

    # The FL node contains a large validation function
    # This runs that function against a variety of input
    # cases.
    def test_fl_node_input_validation(self) -> None:
        # Much of the validation function is concerned with the I/O of inputted components,
        # This function creates a basic command component with specified I/O to aid with testing
        # that validation.
        def create_component_with_io(inputs: List = [], outputs: List = []):
            return command(
                name=f"fake_component",
                display_name="fake component for testing",
                environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5",
                command=('echo "hello world"'),
                distribution={"type": "Pytorch", "process_count_per_instance": 2},
                resources={"instance_count": 2},
                inputs={val: Input(type="number", default=0) for val in inputs},
                outputs={val: Output(type="number", default=0) for val in outputs},
            )

        silo_configs = [
            FederatedLearningSilo(compute="com1", datastore="ds1", inputs={}),
            FederatedLearningSilo(compute="com2", datastore="ds2", inputs={}),
        ]
        agg_compute = None
        agg_ds = None
        silo_comp = create_component_with_io(inputs=["in"], outputs=["out"])
        agg_comp = create_component_with_io(inputs=["in", "in2"], outputs=["out"])
        silo_kwargs = {}
        agg_kwargs = {}
        silo_agg_map = {}
        agg_silo_map = {}
        iters = 1

        # Helper function to simplify the process of repeatedly calling the validation
        # function. Now we only need to modify the input values, then call
        # try_validate() to see how that changes its behavior.
        validate = FLScatterGather.validate_inputs

        def try_validate(raise_error=False):
            return validate(
                silo_configs=silo_configs,
                silo_component=silo_comp,
                aggregation_component=agg_comp,
                shared_silo_kwargs=silo_kwargs,
                aggregation_compute=agg_compute,
                aggregation_datastore=agg_ds,
                aggregation_kwargs=agg_kwargs,
                silo_to_aggregation_argument_map=silo_agg_map,
                aggregation_to_silo_argument_map=agg_silo_map,
                max_iterations=iters,
                raise_error=raise_error,
            )

        # initial check
        validation_result = try_validate()
        assert validation_result.passed

        # Fail if steps don't have static kwargs
        silo_kwargs = {"some_input": 123}
        agg_kwargs = {"another_input": 456}
        validation_result = try_validate()
        assert not validation_result.passed
        assert (
            "shared_silo_kwargs keyword some_input not listed in silo_component's inputs"
            in validation_result.error_messages["shared_silo_kwargs"]
        )
        assert (
            "aggregation_kwargs keyword another_input not listed in aggregation_component's inputs"
            in validation_result.error_messages["aggregation_kwargs"]
        )

        # succeed once inputs have static kwargs
        silo_comp = create_component_with_io(inputs=["some_input"], outputs=["in_out"])
        agg_comp = create_component_with_io(inputs=["another_input"], outputs=["agg_out"])
        validation_result = try_validate()
        assert validation_result.passed

        # fail if steps don't have inputs or outputs mentioned in argument maps
        silo_agg_map = {"silo_output_name": "agg_input_name"}
        agg_silo_map = {"agg_output_name": "silo_input_name"}
        validation_result = try_validate()
        assert (
            "aggregation_to_silo_argument_map key agg_output_name is not a known output of the aggregation component"
            in validation_result.error_messages["aggregation_to_silo_argument_map"]
        )
        assert (
            "aggregation_to_silo_argument_map value silo_input_name is not a known input of the silo component"
            in validation_result.error_messages["aggregation_to_silo_argument_map"]
        )
        assert (
            "silo_to_aggregation_argument_map key silo_output_name is not a known output of the silo component"
            in validation_result.error_messages["silo_to_aggregation_argument_map"]
        )
        assert (
            "silo_to_aggregation_argument_map value agg_input_name is not a known input of the aggregation component"
            in validation_result.error_messages["silo_to_aggregation_argument_map"]
        )
        assert not validation_result.passed

        # succeed once step i/o contains values mentioned in argument maps
        silo_comp = create_component_with_io(
            inputs=["some_input", "silo_input_name"],
            outputs=["in_out", "silo_output_name"],
        )
        agg_comp = create_component_with_io(
            inputs=["another_input", "agg_input_name"],
            outputs=["agg_out", "agg_output_name"],
        )
        validation_result = try_validate()
        assert validation_result.passed

        # Require both datastore and compute to be set for agg step
        agg_ds = "a_datastore"
        validation_result = try_validate()
        assert not validation_result.passed
        assert (
            "aggregation_compute cannot be unset if aggregation_datastore is set"
            in validation_result.error_messages["aggregation_compute"]
        )

        agg_ds = None
        agg_compute = "a_compute"
        validation_result = try_validate()
        assert not validation_result.passed
        assert (
            "aggregation_datastore cannot be unset if aggregation_compute is set"
            in validation_result.error_messages["aggregation_datastore"]
        )

        agg_ds = "a_datastore"
        agg_compute = "a_compute"
        validation_result = try_validate()
        assert validation_result.passed

        # Require number of silo-specific inputs to be consistent per silo
        silo_configs[0] = FederatedLearningSilo(
            compute="com1",
            datastore="ds1",
            inputs={"input1": Input(type=AssetTypes.MLTABLE)},
        )
        validation_result = try_validate()
        assert not validation_result.passed
        assert (
            "Silo at index 1 has is missing inputs named 'input1'" in validation_result.error_messages["silo_configs"]
        )
        assert "Silo at index 1 has 0 inputs" in validation_result.error_messages["silo_configs"]

        silo_configs[1] = FederatedLearningSilo(
            compute="com1",
            datastore="ds1",
            inputs={
                "input1": Input(type=AssetTypes.MLTABLE),
                "input2": Input(type=AssetTypes.MLTABLE),
            },
        )
        validation_result = try_validate()
        assert not validation_result.passed
        assert "Silo at index 1 has 2 inputs" in validation_result.error_messages["silo_configs"]

        silo_configs[1] = FederatedLearningSilo(
            compute="com1",
            datastore="ds1",
            inputs={"input1": Input(type=AssetTypes.MLTABLE)},
        )
        validation_result = try_validate()
        assert validation_result.passed

    # Test 'leaf' case of anchoring.
    # Currently only pipeline steps and
    # command components are anchored.
    # If other components are anchored, we'll need more testing here.
    def test_anchoring_component(self) -> None:
        # A component should have its compute anchored as specified
        # Its output datastores should be assigned to aggregator datastore, if one is inputted
        # If output datastores are already set, and the database doesn't match the
        # orchestrator datatstore, we should get a warning.
        # The local_datastore should be ignored, since there are no in-step outputs for single
        # components.
        command_component = command(
            name="example_comp",
            display_name="test component",
            environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5",
            command=("echo unit test example component. Why was this actually run?"),
            inputs={},
            outputs={"output": Output(type="uri_folder", mode="rw_mount", path="")},
        )
        executed_command_component = command_component()

        compute_name = "a_compute"
        local_ds_name = "local_datastore"
        orch_ds_name = "orchestrator_datastore"

        def try_anchor():
            return FLScatterGather._anchor_step(
                pipeline_step=executed_command_component,
                compute=compute_name,
                internal_datastore=local_ds_name,
                orchestrator_datastore=orch_ds_name,
            )

        warnings = try_anchor()
        assert len(warnings._warnings) == 0
        assert executed_command_component.compute == compute_name
        assert orch_ds_name in executed_command_component.outputs["output"].path

        command_component.outputs["output"].path = "some_path"
        warnings = try_anchor()
        assert "Make sure this is intended" in warnings._warnings[0].message
        assert len(warnings._warnings) == 1
        assert "some_path" not in executed_command_component.outputs["output"].path

    # Ensure that pipeline steps are correctly anchored
    # recursively, setting the values of subcomponents as expected.
    def test_anchoring_pipeline_steps(self) -> None:
        @pipeline(name="test pipeline")
        def test_pipeline_func(x: Input(type="uri_folder")):
            subcomponent1 = command(
                name="example_comp",
                display_name="test component",
                environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5",
                command=("echo unit test example component. Why was this actually run?"),
                inputs={},
                outputs={"output": Output(type="uri_folder", mode="rw_mount", path="")},
            )
            executed_subcomponent1 = subcomponent1()
            subcomponent2 = command(
                name="example_comp",
                display_name="test component",
                environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5",
                command=("echo unit test example component. Why was this actually run?"),
                inputs={"input": Input(type="uri_folder", mode="rw_mount", path="")},
                outputs={
                    "output2": Output(type="uri_folder", mode="rw_mount", path=""),
                    "other_output": Output(type=AssetTypes.MLTABLE, path="this-should-not-change"),
                },
            )
            executed_subcomponent2 = subcomponent2(input=executed_subcomponent1.outputs["output"])
            return {
                "pipeline_output": executed_subcomponent2.outputs["output2"],
                "pipeline_output2": executed_subcomponent2.outputs["other_output"],
            }

        compute_name = "a_compute"
        local_ds_name = "local_datastore"
        orch_ds_name = "orchestrator_datastore"
        executed_pipeline = test_pipeline_func(x=Input(type="uri_folder", mode="mount", path="hello"))
        FLScatterGather._anchor_step(
            pipeline_step=executed_pipeline,
            compute=compute_name,
            internal_datastore=local_ds_name,
            orchestrator_datastore=orch_ds_name,
        )
        assert executed_pipeline.component.jobs["executed_subcomponent1"].compute == compute_name
        assert executed_pipeline.component.jobs["executed_subcomponent2"].compute == compute_name
        assert local_ds_name in executed_pipeline.component.jobs["executed_subcomponent1"].outputs["output"].path
        assert orch_ds_name in executed_pipeline.component.jobs["executed_subcomponent2"].outputs["output2"].path
        assert orch_ds_name in executed_pipeline.outputs["pipeline_output"].path
        assert executed_pipeline.outputs["pipeline_output2"].path == "this-should-not-change"

    def test_import_requirement(self) -> None:
        with pytest.raises(ImportError):
            _check_for_import("not-a-package")
        _check_for_import("mldesigner")
