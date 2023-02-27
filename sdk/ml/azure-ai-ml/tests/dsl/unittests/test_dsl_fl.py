from typing import List
import pytest
from azure.ai.ml import command, Input, Output
from azure.ai.ml.entities._builders.fl_scatter_gather import FLScatterGather, FL_SILO_INDEX_INPUT, FL_ITERATION_INPUT
from azure.ai.ml.entities._assets.federated_learning_silo import FederatedLearningSilo
from azure.ai.ml.constants import AssetTypes

from .._util import _DSL_TIMEOUT_SECOND
@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestDSLPipeline:
    def test_fl_node_creation(self) -> None:
        pass
        '''If the 4, big test files for testing the dsl pipeline are any clue, there's a lot to test
        when decorators are concerned. 
        
        We still need to figure out everything that can be tested, starting at least with a full 
        review of what's testing by the 2000+ line file 'test_dsl_pipeline' and checking out what's
        applicable.

        Separate from that, FL-specific testing will also be needed, mostly to check that the tools we
        offer to represent the scatter-gather loop and silos encode everything correctly for azure to 
        process.
        '''

    def test_fl_node_creation_bad(self) -> None:
        pass

    def test_fl_node_in_pipeline(self) -> None:
        pass

    def test_fl_node_input_validation(self) -> None:
        # Much of the validation function is concerned with the I/O of inputted components,
        # This function creates a basic command component with specified I/O to aid with testing
        # that validation.
        def create_component_with_io(inputs: List=[], outputs: List=[]):
            return command(
                name=f"fake_component",
                display_name="fake component for testing",
                environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5",
                command=('echo "hello world"'),
                distribution={"type": "Pytorch", "process_count_per_instance": 2},
                resources={"instance_count": 2},
                inputs={ val: Input(type="number", default=0) for val in inputs},
                outputs={ val: Output(type="number", default=0) for val in outputs},
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
        pass_iter_to_comps = False
        pass_index_to_comps = False

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
                pass_iteration_to_components = pass_iter_to_comps,
                pass_index_to_silo_components=pass_index_to_comps,
                raise_error=raise_error)
        
        validation_result = try_validate()
        assert validation_result.passed

        pass_index_to_comps = True
        validation_result = try_validate()
        assert not validation_result.passed
        assert " silo component does not" in validation_result.error_messages["pass_index_to_silo_components"]

        silo_comp = create_component_with_io(inputs=[FL_SILO_INDEX_INPUT], outputs=["out"])
        validation_result = try_validate()
        assert validation_result.passed

        pass_iter_to_comps = True
        validation_result = try_validate()
        assert not validation_result.passed
        assert "but the aggregation component does not" in validation_result.error_messages["pass_iteration_to_components"]
        assert "but the silo component does not" in validation_result.error_messages["pass_iteration_to_components"]

        silo_comp = create_component_with_io(inputs=[FL_SILO_INDEX_INPUT, FL_ITERATION_INPUT], outputs=["in_out"])
        agg_comp =  create_component_with_io(inputs=[FL_ITERATION_INPUT], outputs=["agg_out"])
        validation_result = try_validate()
        assert validation_result.passed

        silo_kwargs = {"some_input": 123}
        agg_kwargs = {"another_input": 456}
        validation_result = try_validate()
        assert not validation_result.passed
        assert "shared_silo_kwargs keyword some_input not listed in silo_component's inputs" in validation_result.error_messages["shared_silo_kwargs"]
        assert "aggregation_kwargs keyword another_input not listed in aggregation_component's inputs" in validation_result.error_messages["aggregation_kwargs"]
        

        silo_comp = create_component_with_io(inputs=[FL_SILO_INDEX_INPUT, FL_ITERATION_INPUT, "some_input"], outputs=["in_out"])
        agg_comp =  create_component_with_io(inputs=[FL_ITERATION_INPUT, "another_input"], outputs=["agg_out"])
        validation_result = try_validate()
        assert validation_result.passed

        silo_agg_map = {"silo_output_name": "agg_input_name"}
        agg_silo_map = {"agg_output_name": "silo_input_name"}
        validation_result = try_validate()
        assert "aggregation_to_silo_argument_map key agg_output_name is not a known output of the aggregation component" in validation_result.error_messages["aggregation_to_silo_argument_map"]
        assert "aggregation_to_silo_argument_map value silo_input_name is not a known input of the silo component" in validation_result.error_messages["aggregation_to_silo_argument_map"]
        assert "silo_to_aggregation_argument_map key silo_output_name is not a known output of the silo component" in validation_result.error_messages["silo_to_aggregation_argument_map"]
        assert "silo_to_aggregation_argument_map value agg_input_name is not a known input of the aggregation component" in validation_result.error_messages["silo_to_aggregation_argument_map"]
        assert not validation_result.passed


        silo_comp = create_component_with_io(inputs=[FL_SILO_INDEX_INPUT, FL_ITERATION_INPUT, "some_input", "silo_input_name"], outputs=["in_out", "silo_output_name"])
        agg_comp =  create_component_with_io(inputs=[FL_ITERATION_INPUT, "another_input", "agg_input_name"], outputs=["agg_out", "agg_output_name"])
        validation_result = try_validate()
        assert validation_result.passed

        agg_ds = "a_datastore"
        validation_result = try_validate()
        assert not validation_result.passed
        assert "aggregation_compute cannot be unset if aggregation_datastore is set" in validation_result.error_messages["aggregation_compute"]

        
        agg_ds = None
        agg_compute = "a_compute"
        validation_result = try_validate()
        assert not validation_result.passed
        assert "aggregation_datastore cannot be unset if aggregation_compute is set" in validation_result.error_messages["aggregation_datastore"]

        
        agg_ds = "a_datastore"
        agg_compute = "a_compute"
        validation_result = try_validate()
        assert validation_result.passed

        silo_configs[0] = FederatedLearningSilo(compute="com1", datastore="ds1", inputs={"input1" : Input(type=AssetTypes.MLTABLE)})
        validation_result = try_validate()
        assert not validation_result.passed
        assert "Silo at index 1 has is missing inputs named 'input1'" in validation_result.error_messages["silo_configs"]
        assert "Silo at index 1 has 0 inputs" in validation_result.error_messages["silo_configs"]

        silo_configs[1] = FederatedLearningSilo(compute="com1", datastore="ds1", inputs={"input1" : Input(type=AssetTypes.MLTABLE), "input2" : Input(type=AssetTypes.MLTABLE)})
        validation_result = try_validate()
        assert not validation_result.passed
        assert "Silo at index 1 has 2 inputs" in validation_result.error_messages["silo_configs"]

        
        silo_configs[1] = FederatedLearningSilo(compute="com1", datastore="ds1", inputs={"input1" : Input(type=AssetTypes.MLTABLE)})
        validation_result = try_validate()
        assert validation_result.passed
    
    def test_fl_node_anchoring(self) -> None:
        pass