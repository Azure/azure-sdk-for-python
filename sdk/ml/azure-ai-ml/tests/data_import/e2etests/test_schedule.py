from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml.constants._common import LROConfigurations
from azure.ai.ml.entities._load_functions import load_schedule


@pytest.mark.timeout(1200)
@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test", "mock_code_hash", "mock_asset_name", "mock_component_hash")
@pytest.mark.pipeline_test
class TestSchedule(AzureRecordedTestCase):
    @pytest.mark.parametrize(
        "source_type",
        [
            ("database"),
            ("file_system"),
        ],
    )
    def test_create_schedule_data_import(self, client: MLClient, randstr: Callable[[], str], source_type: str):
        params_override = [{"name": randstr("name")}]
        test_path = "./tests/test_configs/data_import/schedule_data_import_" + source_type + ".yml"
        schedule = load_schedule(test_path, params_override=params_override)
        rest_schedule = client.schedules.begin_create_or_update(schedule).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )
        rest_schedule_dict = rest_schedule._to_dict()
        assert rest_schedule.name == schedule.name
        assert rest_schedule_dict["trigger"]["type"] == "cron"
        assert rest_schedule_dict["import_data"]["source"]["type"] == source_type
        assert rest_schedule_dict["import_data"]["path"] == "azureml://datastores/workspaceblobstore/paths/{name}"

        if source_type == "file_system":
            assert rest_schedule_dict["import_data"]["name"] == "my_s3_asset"
            assert rest_schedule_dict["import_data"]["type"] == "uri_folder"
            assert rest_schedule_dict["import_data"]["source"]["connection"] == "azureml:my_s3_connection"
            assert rest_schedule_dict["import_data"]["source"]["path"] == "test1/*"
        else:
            assert rest_schedule_dict["import_data"]["name"] == "my_azuresqldb_asset"
            assert rest_schedule_dict["import_data"]["type"] == "mltable"
            assert rest_schedule_dict["import_data"]["source"]["connection"] == "azureml:my_azuresqldb_connection"
            assert rest_schedule_dict["import_data"]["source"]["query"] == "select * from region"
