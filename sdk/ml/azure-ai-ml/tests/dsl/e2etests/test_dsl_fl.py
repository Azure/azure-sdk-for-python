import pytest
from pathlib import Path
from devtools_testutils import AzureRecordedTestCase, is_live
from azure.core.exceptions import ResourceNotFoundError
from .._util import _DSL_TIMEOUT_SECOND
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD
from azure.ai.ml import Input, load_component
from typing import Callable
from azure.ai.ml.dsl._fl_scatter_gather_node import fl_scatter_gather
from azure.ai.ml.entities._assets.federated_learning_silo import FederatedLearningSilo
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities._credentials import (
    IdentityConfiguration,
    IdentityConfigurationType,
    ManagedIdentityConfiguration,
)
from azure.ai.ml.dsl import pipeline
import os
from azure.ai.ml import (
    MLClient,
)


# RESOURCE NOTES - As an e2e test file, this file makes and references real AML resources.
# All resources references by this file are contained within the following:
# subscription: data science VM Team (DSVM)
# resource group: fl-e2e-testing-rg
# workspace: fl-e2e-testing-ws
# If you're running this test locally in live mode, make sure you've set the above values in
# your .env file.
# resources of note:
# - multiple storage containers
# - multiple computes with varying managed identities to allow access to different storage containers
@pytest.mark.timeout(timeout=_DSL_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.core_sdk_test
class TestDSLPipeline(AzureRecordedTestCase):
    # DEV NOTE: This test expects a lot of resources to already exist in AML. The initial implementation
    # of this test implemented all of these thigns under the 'fl-e2e-testing-rg' resource group and
    # the 'fl-e2e-testing-ws' workspace inside that RG.
    # The needed resources are:
    # - In the workspace's storage account, 3 containers named 'silo-container1', 'silo-container23',
    #       and 'agg-container'. Each container needs to have assigned the blob owner permission
    #       to the 'test-msi-id' managed identity
    # - 4 compute clusters in the workspace named siloCompute1/2/3 and aggCompute. Each of which
    #       has been assigned the 'test-msi-id' ID
    # - 4 datastores connected to the aforementioned storage containers named silo_datastore1/2/3 and
    #       agg_datastore.
    @pytest.mark.skipif(
        condition=not is_live(),
        reason=(
            "TODO (2235034) The critical call to `client.jobs.create_or_update` seems to make different"
            + "API calls in playback mode compared to recording mode"
        ),
    )
    def test_fl_pipeline(
        self,
        client: MLClient,
        federated_learning_components_folder: Path,
        federated_learning_local_data_folder: Path,
    ) -> None:
        id = IdentityConfiguration(
            type=IdentityConfigurationType.MANAGED,
            user_assigned_identities=[ManagedIdentityConfiguration(client_id="3adff742-0142-45a6-8142-3d94f944cafb")],
        )

        # To support dsl pipeline kwargs
        os.environ["AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED"] = "True"
        compute_names = [
            "siloCompute1",
            "siloCompute2",
            "siloCompute3",
            "aggCompute",
        ]
        computes = []
        for name in compute_names:
            try:
                extant_compute = client.compute.get(name)
                print(f"Found existing compute '{name}', using that instead of creating it.")
                computes.append(extant_compute)
            except ResourceNotFoundError as e:
                raise (e)

        datastore_names = [
            "silo_datastore1",
            "silo_datastore2",
            "silo_datastore3",
            "agg_datastore",
        ]

        datastores = []
        for datastore_name in datastore_names:
            try:
                extant_ds = client.datastores.get(datastore_name)
                print(f"Found existing datastore '{datastore_name}', using that instead of creating it.")
                datastores.append(extant_ds)
            except ResourceNotFoundError as e:
                raise (e)

        # Load components from local configs
        preprocessing_component = load_component(
            source=os.path.join(federated_learning_components_folder, "preprocessing", "spec.yaml")
        )

        training_component = load_component(
            source=os.path.join(federated_learning_components_folder, "training", "spec.yaml")
        )

        aggregate_component = load_component(
            source=os.path.join(federated_learning_components_folder, "aggregate", "spec.yaml")
        )

        # Use a nested pipeline for the silo step
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

        # Use a component directly for the agg step
        aggregation_step = aggregate_component

        silo_configs = [
            FederatedLearningSilo(
                compute=computes[0].name,
                datastore=datastores[0].name,
                inputs={
                    "raw_train_data": Input(
                        type=AssetTypes.URI_FILE,
                        mode="direct",
                        path=os.path.join(federated_learning_local_data_folder, "silo1_input1.txt"),
                        datastore=datastores[0].name,
                    ),
                    "raw_test_data": Input(
                        type=AssetTypes.URI_FILE,
                        mode="direct",
                        path=os.path.join(federated_learning_local_data_folder, "silo1_input2.txt"),
                        datastore=datastores[0].name,
                    ),
                },
            ),
            FederatedLearningSilo(
                compute=computes[1].name,
                datastore=datastores[1].name,
                inputs={
                    "raw_train_data": Input(
                        type=AssetTypes.URI_FILE,
                        mode="mount",
                        path=os.path.join(federated_learning_local_data_folder, "silo2_input1.txt"),
                        datastore=datastores[1].name,
                    ),
                    "raw_test_data": Input(
                        type=AssetTypes.URI_FILE,
                        mode="direct",
                        path=os.path.join(federated_learning_local_data_folder, "silo2_input2.txt"),
                        datastore=datastores[1].name,
                    ),
                },
            ),
            FederatedLearningSilo(
                compute=computes[2].name,
                datastore=datastores[2].name,
                inputs={
                    "raw_train_data": Input(
                        type=AssetTypes.URI_FILE,
                        mode="mount",
                        path=os.path.join(federated_learning_local_data_folder, "silo3_input1.txt"),
                        datastore=datastores[2].name,
                    ),
                    "raw_test_data": Input(
                        type=AssetTypes.URI_FILE,
                        mode="mount",
                        path=os.path.join(federated_learning_local_data_folder, "silo3_input2.txt"),
                        datastore=datastores[2].name,
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
        aggregation_compute = computes[3].name
        aggregation_datastore = datastores[3].name

        # Define the fl pipeline
        fl_node = fl_scatter_gather(
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

        # create and submit the pipeline job
        submitted_pipeline_job = client.jobs.create_or_update(
            fl_node.scatter_gather_graph, experiment_name="example_fl_pipeline"
        )
        print("Submitted pipeline job: {}".format(submitted_pipeline_job.id))
        subgraph = submitted_pipeline_job.component.jobs

        # Unfortunately executed pipelines don't return interior values of sub-pipelines,
        # so we can't inspect internal datastores or computes in silo steps
        assert "scatter_gather_body" in subgraph
        scatter_gather_body = subgraph["scatter_gather_body"]
        assert scatter_gather_body.type == "pipeline"
        assert all(silo_input in scatter_gather_body.inputs for silo_input in silo_kwargs)
        assert all(silo_input in scatter_gather_body.inputs for silo_input in aggregation_to_silo_argument_map.values())
        assert all(agg_output in scatter_gather_body.outputs for agg_output in aggregation_to_silo_argument_map)
