# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import datetime
import time
from pathlib import Path
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import MLClient
from azure.ai.ml.entities import FeatureSet, MaterializationComputeResource, MaterializationSettings
from azure.ai.ml.entities._assets._artifacts.feature_set import FeatureSet
from azure.ai.ml.entities._load_functions import load_feature_set
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller


@pytest.mark.e2etest
@pytest.mark.data_experiences_test
@pytest.mark.usefixtures("recorded_test", "mock_code_hash")
class TestFeatureSet(AzureRecordedTestCase):
    def test_create_and_get(self, feature_store_client: MLClient, tmp_path: Path, randstr: Callable[[], str]) -> None:
        fset_name = f"e2etest_{randstr('fset_name')}"
        fset_description = "Feature set description"
        fs_entity_name = "e2etest_fs_entity"
        version = "1"

        params_override = [
            {"name": fset_name},
            {"version": version},
            {"description": fset_description},
        ]

        def feature_set_validation(fset: FeatureSet):
            fset.entities = [f"azureml:{fs_entity_name}:{version}"]
            fset_poller = feature_store_client.feature_sets.begin_create_or_update(featureset=fset)
            assert isinstance(fset_poller, LROPoller)
            fset = fset_poller.result()
            assert isinstance(fset, FeatureSet)
            assert fset.name == fset_name
            assert fset.description == fset_description

        fset = verify_entity_load_and_dump(
            load_feature_set,
            feature_set_validation,
            "./tests/test_configs/feature_set/feature_set_e2e.yaml",
            params_override=params_override,
        )[0]

        fset_list = feature_store_client.feature_sets.list(name=fset_name)
        assert isinstance(fset_list, ItemPaged)

        fset = feature_store_client.feature_sets.get(name=fset_name, version=version)
        assert isinstance(fset, FeatureSet)
        assert fset.name == fset_name

    # ---------------------------------------------------------------------------------------------------------------#
    # NOTE Please enable materialization store on test featurestore 'sdk_vnext_cli_fs' to run this test in live mode.
    # ---------------------------------------------------------------------------------------------------------------#
    @pytest.mark.skip(reason="request header size being too large.")
    def test_list_materialization_jobs(
        self, feature_store_client: MLClient, tmp_path: Path, randstr: Callable[[], str]
    ) -> None:
        fset_name = f"e2etest_fset_jobs"
        fset_description = "Feature set description"
        fs_entity_name = "e2etest_fs_entity"
        version = "1"

        params_override = [
            {"name": fset_name},
            {"version": version},
            {"description": fset_description},
        ]

        def feature_set_validation(fset: FeatureSet):
            fset.entities = [f"azureml:{fs_entity_name}:{version}"]
            fset.materialization_settings = MaterializationSettings(
                offline_enabled=True,
                spark_configuration={
                    "spark.driver.cores": 2,
                    "spark.driver.memory": "18g",
                    "spark.executor.cores": 4,
                    "spark.executor.memory": "18g",
                    "spark.executor.instances": 5,
                },
                resource=MaterializationComputeResource(instance_type="standard_e4s_v3"),
            )
            fset_poller = feature_store_client.feature_sets.begin_create_or_update(featureset=fset)
            assert isinstance(fset_poller, LROPoller)
            fset = fset_poller.result()
            assert isinstance(fset, FeatureSet)

        verify_entity_load_and_dump(
            load_feature_set,
            feature_set_validation,
            "./tests/test_configs/feature_set/feature_set_e2e.yaml",
            params_override=params_override,
        )[0]

        # set up 11 backfill jobs
        if is_live():
            for i in range(0, 11):
                backfill_poller = feature_store_client.feature_sets.begin_backfill(
                    name=fset_name,
                    version=version,
                    # account for source delay
                    feature_window_start_time=datetime.datetime.now() - datetime.timedelta(i + 1 + 2),
                    feature_window_end_time=datetime.datetime.now() - datetime.timedelta(i + 2),
                    data_status=["None", "Complete"],
                )
                assert isinstance(backfill_poller, LROPoller)
                backfill_response = backfill_poller.result()
                # TODO: wait for job to complete or cancel them manually
                time.sleep(900)  # 15 mins

        materialization_jobs = feature_store_client.feature_sets.list_materialization_operations(
            name=fset_name, version=version
        )
        assert materialization_jobs is not None
        i = 0
        for jobs in materialization_jobs:
            assert jobs.name is not None
            i = i + 1
            if i == 11:
                break
