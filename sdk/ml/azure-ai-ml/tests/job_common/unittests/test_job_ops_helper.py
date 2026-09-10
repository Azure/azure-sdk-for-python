import re
import time
from collections import OrderedDict
from io import StringIO
from typing import Dict
from unittest.mock import Mock

import pytest
from mock import mock_open, patch

from azure.ai.ml._restclient.dataset_dataplane.models import BatchDataUriResponse, DataUriV2Response
from azure.ai.ml._restclient.model_dataplane.models import BatchModelPathResponseDto, ModelPathResponseDto
from azure.ai.ml._restclient.runhistory.models import (
    GetRunDataResult,
    Run,
    RunDetails,
    RunDetailsWarning,
    TypedAssetReference,
)
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.operations._dataset_dataplane_operations import DatasetDataplaneOperations
from azure.ai.ml.operations._job_ops_helper import (
    _get_sorted_filtered_logs,
    get_job_output_uris_from_dataplane,
    has_pat_token,
    _incremental_print,
    list_logs,
    stream_logs_until_completion,
)
from azure.ai.ml.operations._model_dataplane_operations import ModelDataplaneOperations
from azure.ai.ml.operations._run_operations import RunOperations

from .test_vcr_utils import before_record_cb


DATA_OUTPUT_ASSET_ID = "azureml://locations/eastus/workspaces/00000/data/azureml_dummy_output_data/versions/1"
MODEL_OUTPUT_ASSET_ID = "azureml://locations/eastus/workspaces/00000/models/azureml_dummy_output_model/versions/1"
DATA_OUTPUT_URI = "azureml://datastores/workspaceblobstore/paths/azureml/dummy/forecast_data/"
MODEL_OUTPUT_URI = "azureml://datastores/workspaceblobstore/paths/azureml/dummy/trained_model/"


def build_run_operations(outputs: Dict[str, TypedAssetReference]) -> Mock:
    run_operations = Mock()
    run_operations.get_run_data.return_value = GetRunDataResult(run_metadata=Run(outputs=outputs))
    return run_operations


def build_dataset_dataplane_operations(uris: Dict[str, str]) -> Mock:
    dataset_dataplane_operations = Mock()
    dataset_dataplane_operations.get_batch_dataset_uris.return_value = BatchDataUriResponse(
        values_property={asset_id: DataUriV2Response(uri=uri) for asset_id, uri in uris.items()}
    )
    return dataset_dataplane_operations


def build_model_dataplane_operations(paths: Dict[str, str]) -> Mock:
    model_dataplane_operations = Mock()
    model_dataplane_operations.get_batch_model_uris.return_value = BatchModelPathResponseDto(
        values_property={asset_id: ModelPathResponseDto(path=path) for asset_id, path in paths.items()}
    )
    return model_dataplane_operations


class DummyJob:
    class InteractionEndpoint:
        def __init__(self, **kwargs):
            self.endpoint = "testurl"

    class Properties:
        def __init__(self, **kwargs):
            super().__init__()
            self.experiment_name = "dummy_exp"
            self.services = {"Studio": DummyJob.InteractionEndpoint()}
            self.job_type = "Command"

    def __init__(self, **kwargs):
        super().__init__()
        self.name = "dummy"
        self.properties = DummyJob.Properties()


def fake_read():
    return mock_open(read_data="{}")


@pytest.fixture
def mock__commands():
    m = Mock(name="_commands")
    mock_run_history_facade = patch.dict("sys.modules", {"azureml._execution": m})
    mock_run_history_facade.start()
    yield m
    mock_run_history_facade.stop()


@pytest.fixture
def mock_time(request):
    p = patch("azure.ai.ml.operations._job_ops_helper.time")
    yield p.start()
    p.stop()


@pytest.fixture
def mock_run_operations(mock_workspace_scope: OperationScope, mock_aml_services_run_history: Mock) -> RunOperations:
    yield RunOperations(mock_workspace_scope, mock_aml_services_run_history)


@pytest.fixture
def mock_dataset_dataplane_operations(
    mock_workspace_scope: OperationScope, mock_operation_config: OperationConfig
) -> DatasetDataplaneOperations:
    yield DatasetDataplaneOperations(mock_workspace_scope, mock_operation_config, Mock())


@pytest.fixture
def mock_model_dataplane_operations(
    mock_workspace_scope: OperationScope, mock_operation_config: OperationConfig
) -> ModelDataplaneOperations:
    yield ModelDataplaneOperations(mock_workspace_scope, mock_operation_config, Mock())


@pytest.mark.unittest
@pytest.mark.training_experiences_test
class TestJobOpsHelper:
    def test_has_pat_token(self) -> None:
        assert has_pat_token("https://dev.azure.com/mypattoken@company_machineName/project-name/_git/repo_name")
        assert has_pat_token("https://mypattoken@dev.azure.com/<organization>/<project>/_git/<repo>")
        assert not has_pat_token("https://dev.azure.com/organization/project/_apis/pipelines/1/runs")
        assert not has_pat_token("https://learn.microsoft.com/en-us/ai/?tabs=developer")

    @pytest.mark.parametrize(
        "data_type,model_type",
        [
            # RunHistory reports the type of a job's outputs in PascalCase
            ("UriFolder", "CustomModel"),
            ("UriFile", "MLFlowModel"),
            ("MLTable", "TritonModel"),
            # while the control plane spells the same types in snake_case
            ("uri_folder", "custom_model"),
            ("uri_file", "mlflow_model"),
            ("mltable", "triton_model"),
        ],
    )
    def test_get_job_output_uris_from_dataplane(self, data_type: str, model_type: str) -> None:
        run_operations = build_run_operations(
            {
                "forecast_data": TypedAssetReference(asset_id=DATA_OUTPUT_ASSET_ID, type=data_type),
                "trained_model": TypedAssetReference(asset_id=MODEL_OUTPUT_ASSET_ID, type=model_type),
            }
        )

        outputs = get_job_output_uris_from_dataplane(
            "dummy",
            run_operations,
            build_dataset_dataplane_operations({DATA_OUTPUT_ASSET_ID: DATA_OUTPUT_URI}),
            build_model_dataplane_operations({MODEL_OUTPUT_ASSET_ID: MODEL_OUTPUT_URI}),
        )

        assert outputs == {"forecast_data": DATA_OUTPUT_URI, "trained_model": MODEL_OUTPUT_URI}

    def test_get_job_output_uris_from_dataplane_with_output_name(self) -> None:
        run_operations = build_run_operations(
            {"forecast_data": TypedAssetReference(asset_id=DATA_OUTPUT_ASSET_ID, type="UriFolder")}
        )
        dataset_dataplane_operations = build_dataset_dataplane_operations({DATA_OUTPUT_ASSET_ID: DATA_OUTPUT_URI})

        outputs = get_job_output_uris_from_dataplane(
            "dummy",
            run_operations,
            dataset_dataplane_operations,
            None,
            output_names="forecast_data",
        )

        assert outputs == {"forecast_data": DATA_OUTPUT_URI}
        dataset_dataplane_operations.get_batch_dataset_uris.assert_called_once_with([DATA_OUTPUT_ASSET_ID])

    def test_get_job_output_uris_from_dataplane_skips_unknown_types(self) -> None:
        run_operations = build_run_operations(
            {
                "unknown_type": TypedAssetReference(asset_id=DATA_OUTPUT_ASSET_ID, type="SomethingElse"),
                "no_type": TypedAssetReference(asset_id=MODEL_OUTPUT_ASSET_ID),
            }
        )
        dataset_dataplane_operations = build_dataset_dataplane_operations({})
        model_dataplane_operations = build_model_dataplane_operations({})

        outputs = get_job_output_uris_from_dataplane(
            "dummy",
            run_operations,
            dataset_dataplane_operations,
            model_dataplane_operations,
        )

        assert outputs == {}
        dataset_dataplane_operations.get_batch_dataset_uris.assert_not_called()
        model_dataplane_operations.get_batch_model_uris.assert_not_called()

    def test_get_job_output_uris_from_dataplane_requests_asset_ids(
        self,
        mock_dataset_dataplane_operations: DatasetDataplaneOperations,
        mock_model_dataplane_operations: ModelDataplaneOperations,
    ) -> None:
        mock_dataset_dataplane_operations._operation.batch_get_resolved_uris.return_value = BatchDataUriResponse(
            values_property={DATA_OUTPUT_ASSET_ID: DataUriV2Response(uri=DATA_OUTPUT_URI)}
        )
        mock_model_dataplane_operations._operation.batch_get_resolved_uris.return_value = BatchModelPathResponseDto(
            values_property={MODEL_OUTPUT_ASSET_ID: ModelPathResponseDto(path=MODEL_OUTPUT_URI)}
        )
        run_operations = build_run_operations(
            {
                "forecast_data": TypedAssetReference(asset_id=DATA_OUTPUT_ASSET_ID, type="UriFolder"),
                "trained_model": TypedAssetReference(asset_id=MODEL_OUTPUT_ASSET_ID, type="CustomModel"),
            }
        )

        outputs = get_job_output_uris_from_dataplane(
            "dummy",
            run_operations,
            mock_dataset_dataplane_operations,
            mock_model_dataplane_operations,
        )

        assert outputs == {"forecast_data": DATA_OUTPUT_URI, "trained_model": MODEL_OUTPUT_URI}
        dataset_request = mock_dataset_dataplane_operations._operation.batch_get_resolved_uris.call_args[1]["body"]
        assert dataset_request.values_property == [DATA_OUTPUT_ASSET_ID]
        model_request = mock_model_dataplane_operations._operation.batch_get_resolved_uris.call_args[1]["body"]
        assert model_request.values_property == [MODEL_OUTPUT_ASSET_ID]


@pytest.mark.skip("TODO 1907352: Relies on a missing VCR.py recording + test suite needs to be reworked")
@pytest.mark.unittest
@pytest.mark.training_experiences_test
class TestJobLogManager:
    def test_wait_for_completion_with_output(self, mock_run_operations):
        dummy_job = DummyJob()
        with patch.object(
            RunOperations,
            "get_run_details",
            side_effect=[
                RunDetails(status="Finalizing", log_files={"log1": "Log", "log2": "log"}),
                RunDetails(status="Completed", log_files={"log1": "Log", "log2": "log"}),
            ],
        ) as get_run_mock:
            stream_logs_until_completion(mock_run_operations, dummy_job)
            get_run_mock.assert_called()

    def test_wait_for_completion_with_error_silent(self, mock_run_operations):
        dummy_job = DummyJob()
        with patch.object(
            RunOperations,
            "get_run_details",
            return_value=RunDetails(status="Failed", warnings=[RunDetailsWarning(message="bad luck")]),
        ) as get_run_mock:
            stream_logs_until_completion(mock_run_operations, dummy_job, None, False)
            get_run_mock.assert_called_once()

    def test_wait_for_completion_with_error_raise(self, mock_run_operations):
        dummy_job = DummyJob()
        with patch.object(RunOperations, "get_run_details", return_value=RunDetails(status="Failed")) as get_run_mock:
            with pytest.raises(Exception):
                stream_logs_until_completion(mock_run_operations, dummy_job)
            get_run_mock.assert_called_once()

    # The list of logs that should be streamed, if you need to recreate,
    # you can just copy and paste the logFiles section from the Raw run JSON on the UI,
    # then keep here only the ones we stream
    _streamable_log_files_urls = OrderedDict(
        {
            "azureml-logs/55_azureml-execution-tvmps_f712ea79c8fca9c3c7f41774b414e867a0854377c8e411b095f30dd68f6d6027_d.txt": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/55_azureml-execution-tvmps_f712ea79c8fca9c3c7f41774b414e867a0854377c8e411b095f30dd68f6d6027_d.txt?sv=2019-02-02&sr=b&sig=2B9oQEbsUwKZzw1eTUiyLJy64DRC%2BVOjv9lRb8Jx%2FLM%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
            "azureml-logs/65_job_prep-tvmps_f712ea79c8fca9c3c7f41774b414e867a0854377c8e411b095f30dd68f6d6027_d.txt": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/65_job_prep-tvmps_f712ea79c8fca9c3c7f41774b414e867a0854377c8e411b095f30dd68f6d6027_d.txt?sv=2019-02-02&sr=b&sig=2E1x1mUWF5Y8VD1e0yMqEZeWct4vngjES%2FJ3SFzKKxU%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
            "azureml-logs/70_driver_log-worker-0.txt": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/70_driver_log-worker-0.txt?sv=2019-02-02&sr=b&sig=8lXLfLMqGaQ7VNGLCKkQ%2BbdebJcyEFCJzNStYCRuVZc%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
            "azureml-logs/75_job_post-tvmps_f712ea79c8fca9c3c7f41774b414e867a0854377c8e411b095f30dd68f6d6027_d.txt": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/75_job_post-tvmps_f712ea79c8fca9c3c7f41774b414e867a0854377c8e411b095f30dd68f6d6027_d.txt?sv=2019-02-02&sr=b&sig=9YR6A64Tuq0E7KsgzPX7atqJ33eGjaJ8QeRaNaQ1%2BL4%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
        }
    )

    # The list of logs that should NOT be streamed, if you need to recreate,
    # you can just copy and paste the logFiles section from the Raw run JSON on the UI,
    # then keep here only the ones we shouldn't stream
    _additional_log_files_urls = {
        "azureml-logs/process_info.json": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/process_info.json?sv=2019-02-02&sr=b&sig=wn2pW00%2F86Qlo3NWOokMVGmaeModJNyHlIP5dDI4zqk%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
        "azureml-logs/process_status.json": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/process_status.json?sv=2019-02-02&sr=b&sig=FDFzfqtn9iYq2FMb5SOBGBu91k%2B8LQITcRiYYyLtDHs%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
        "logs/azureml/job_prep_azureml.log": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/logs/azureml/job_prep_azureml.log?sv=2019-02-02&sr=b&sig=td0HUXBar%2FYv%2FhZiSdlPR516OH8bCMiBN3yH6dCSHvk%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
        "logs/azureml/job_release_azureml.log": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/logs/azureml/job_release_azureml.log?sv=2019-02-02&sr=b&sig=BeeRya%2FFZhqCNBk0hCJrks7%2Bejg9qTCFe5FNnf%2BUJyk%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
        "logs/azureml/worker0_373_azureml.log": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/logs/azureml/worker0_373_azureml.log?sv=2019-02-02&sr=b&sig=ySxUJjd1lqi%2FskcMfAYYFQ%2FyUQALbV0WH7jYtf%2FXaKk%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
    }

    _common_runtime_log_urls = {
        "user_logs/std_log.txt": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/process_info.json?sv=2019-02-02&sr=b&sig=wn2pW00%2F86Qlo3NWOokMVGmaeModJNyHlIP5dDI4zqk%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
        "azureml-logs/lifecycler/lifecycler.log": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/process_info.json?sv=2019-02-02&sr=b&sig=wn2pW00%2F86Qlo3NWOokMVGmaeModJNyHlIP5dDI4zqk%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
    }

    _common_runtime_mpi_urls = {
        "user_logs/std_log_process_00.txt": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/process_info.json?sv=2019-02-02&sr=b&sig=wn2pW00%2F86Qlo3NWOokMVGmaeModJNyHlIP5dDI4zqk%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
        "user_logs/std_log_process_01.txt": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/process_info.json?sv=2019-02-02&sr=b&sig=wn2pW00%2F86Qlo3NWOokMVGmaeModJNyHlIP5dDI4zqk%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
        "user_logs/std_log_process_02.txt": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/process_info.json?sv=2019-02-02&sr=b&sig=wn2pW00%2F86Qlo3NWOokMVGmaeModJNyHlIP5dDI4zqk%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
        "user_logs/std_log_process_03.txt": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/process_info.json?sv=2019-02-02&sr=b&sig=wn2pW00%2F86Qlo3NWOokMVGmaeModJNyHlIP5dDI4zqk%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
        "user_logs/std_log_process_04.txt": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/process_info.json?sv=2019-02-02&sr=b&sig=wn2pW00%2F86Qlo3NWOokMVGmaeModJNyHlIP5dDI4zqk%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
    }

    _common_runtime_tensorflow_urls = {
        "user_logs/std_log_node_00_ps.txt": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/process_info.json?sv=2019-02-02&sr=b&sig=wn2pW00%2F86Qlo3NWOokMVGmaeModJNyHlIP5dDI4zqk%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
        "user_logs/std_log_node_01_ps.txt": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/process_info.json?sv=2019-02-02&sr=b&sig=wn2pW00%2F86Qlo3NWOokMVGmaeModJNyHlIP5dDI4zqk%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
        "user_logs/std_log_node_00_worker.txt": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/process_info.json?sv=2019-02-02&sr=b&sig=wn2pW00%2F86Qlo3NWOokMVGmaeModJNyHlIP5dDI4zqk%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
        "user_logs/std_log_node_01_worker.txt": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/process_info.json?sv=2019-02-02&sr=b&sig=wn2pW00%2F86Qlo3NWOokMVGmaeModJNyHlIP5dDI4zqk%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
        "user_logs/std_log_node_02_worker.txt": "https://rihorn24316837458.blob.core.windows.net/azureml/ExperimentRun/dcid.1a9952e7-f173-45c0-bd61-3cd591498bdf/azureml-logs/process_info.json?sv=2019-02-02&sr=b&sig=wn2pW00%2F86Qlo3NWOokMVGmaeModJNyHlIP5dDI4zqk%3D&skoid=e3f42e2c-d581-4b65-a966-631cfa961328&sktid=72f988bf-86f1-41af-91ab-2d7cd011db47&skt=2021-05-03T13%3A11%3A21Z&ske=2021-05-04T08%3A32%3A18Z&sks=b&skv=2019-02-02&st=2021-05-03T13%3A45%3A30Z&se=2021-05-03T21%3A55%3A30Z&sp=r",
    }

    # Method to create a RunDetails based on the provided status,
    # the number of streamable files to include, and if whether to add or not
    # non-streamable log files
    def _get_run_details_dto(
        self, status="Finalizing", number_of_streamable_log_files=0, include_additional_log_files=False
    ) -> RunDetails:
        keys = self._streamable_log_files_urls.keys()

        # Check if there are enough streamable log files
        if number_of_streamable_log_files > len(keys):
            raise Exception(f"There are less than {number_of_streamable_log_files}")

        # Keep only the first number_of_streamable_log_files logs
        log_files = {}
        for key in keys:
            log_files[key] = self._streamable_log_files_urls[key]
            number_of_streamable_log_files -= 1
            if not number_of_streamable_log_files:
                break

        # Add the additional logs if specified
        if include_additional_log_files:
            log_files.update(self._additional_log_files_urls)

        return RunDetails(status=status, log_files=log_files)

    # Helper method to test that logs will be streamed comprehensively
    # and in predictable order independently of the sequence of run details.
    # Logs could be delivered at different pace after subsequent calls to get details
    def _test_stream_logs_helper(self, mock_run_operations, run_details_sequence=[]) -> None:
        my_vcr = vcr.VCR(before_record=before_record_cb)

        with patch("sys.stdout", new=StringIO()) as fake_out, patch.object(
            RunOperations, "get_run_details", side_effect=run_details_sequence
        ) as get_run_mock, patch.object(
            time,
            "sleep",
        ) as fake_time, my_vcr.use_cassette(
            "cassettes/test_stream_logs.yaml"
        ):
            stream_logs_until_completion(mock_run_operations, DummyJob())

            # get_run_mock was called, and all the sequence of run details was consumed
            get_run_mock.assert_called()
            assert get_run_mock.call_count == len(run_details_sequence)

            # while streamed, we waited in between each call to get run details
            fake_time.assert_called()
            assert fake_time.call_count == len(run_details_sequence) - 1

            # Regext to checking on the 'Streaming <log name>' message
            reg_exp = re.compile(r"Streaming ([\S]*)")

            output = fake_out.getvalue()
            list_of_logs = list(self._streamable_log_files_urls.keys())

            # Check that all the logs were streamed
            assert reg_exp.findall(output) == list_of_logs

            # Check there were no duplicates
            assert len(list_of_logs) == len(set(list_of_logs))

    def test_list_logs(self, mock_run_operations) -> None:
        with patch.object(
            RunOperations,
            "get_run_details",
            side_effect=[self._get_run_details_dto(status="Completed", number_of_streamable_log_files=3)],
        ) as get_run_mock:
            output = list_logs(mock_run_operations, DummyJob())
            get_run_mock.assert_called()
            assert len(output.items()) == 3

    # Method to test the golden path, a new log was added on each call to get run details
    @pytest.mark.vcr()
    def test_stream_logs_golden_path(self, mock_run_operations) -> None:
        run_details_sequence = [
            self._get_run_details_dto(status="Running"),
            self._get_run_details_dto(status="Finalizing", number_of_streamable_log_files=1),
            self._get_run_details_dto(status="Finalizing", number_of_streamable_log_files=2),
            self._get_run_details_dto(status="Finalizing", number_of_streamable_log_files=3),
            self._get_run_details_dto(status="Finalizing", number_of_streamable_log_files=4),
            self._get_run_details_dto(
                status="Completed", number_of_streamable_log_files=4, include_additional_log_files=True
            ),
        ]

        self._test_stream_logs_helper(mock_run_operations, run_details_sequence=run_details_sequence)

    # Method to test when all the logs were available at the same time
    @pytest.mark.vcr()
    def test_stream_logs_arriving_all_together(self, mock_run_operations) -> None:
        run_details_sequence = [
            self._get_run_details_dto(status="Running"),
            self._get_run_details_dto(status="Finalizing", number_of_streamable_log_files=4),
            self._get_run_details_dto(
                status="Completed", number_of_streamable_log_files=4, include_additional_log_files=True
            ),
        ]

        self._test_stream_logs_helper(mock_run_operations, run_details_sequence=run_details_sequence)

    # Method to test when the logs became available in batches of 2
    @pytest.mark.vcr()
    def test_stream_logs_arriving_in_batches(self, mock_run_operations) -> None:
        run_details_sequence = [
            self._get_run_details_dto(status="Running"),
            self._get_run_details_dto(status="Finalizing", number_of_streamable_log_files=2),
            self._get_run_details_dto(status="Finalizing", number_of_streamable_log_files=4),
            self._get_run_details_dto(
                status="Completed", number_of_streamable_log_files=4, include_additional_log_files=True
            ),
        ]

        self._test_stream_logs_helper(mock_run_operations, run_details_sequence=run_details_sequence)

    def test_get_streamable_logs_common_runtime_folder_structure(self) -> None:
        output = _get_sorted_filtered_logs(self._common_runtime_log_urls, "Command")
        assert len(output) == 1
        assert output[0] == "user_logs/std_log.txt"

    def test_get_all_logs_common_runtime_folder_structure(self) -> None:
        output = _get_sorted_filtered_logs(self._common_runtime_log_urls, "Command", {}, False)
        assert len(output) == 1
        assert output[0] == "user_logs/std_log.txt"

    def test_get_streamable_logs_common_runtime_mpi(self) -> None:
        output = _get_sorted_filtered_logs(self._common_runtime_mpi_urls, "Command")
        assert len(output) == 1
        assert output[0] == "user_logs/std_log_process_00.txt"

    def test_get_all_logs_common_runtime_mpi(self) -> None:
        output = _get_sorted_filtered_logs(self._common_runtime_mpi_urls, "Command", {}, False)
        assert len(output) == 5

    def test_get_streamable_logs_common_runtime_tensorflow(self) -> None:
        output = _get_sorted_filtered_logs(self._common_runtime_tensorflow_urls, "Command")
        assert len(output) == 1
        assert output[0] == "user_logs/std_log_node_00_ps.txt"

    def test_get_all_logs_common_runtime_tensorflow(self) -> None:
        output = _get_sorted_filtered_logs(self._common_runtime_tensorflow_urls, "Command", {}, False)
        assert len(output) == 5

    def test_stream_printing(self) -> None:
        log_name = "55_log_test"
        log_content = "line1\nline2\nline3\n"
        stream = StringIO()
        processed_logs: Dict[str, int] = {}
        _incremental_print(log_content, processed_logs, log_name, stream)
        # should contain the length of the log (3) + the header lines (4)
        assert len(stream.getvalue().splitlines()) == 7
        assert processed_logs[log_name] == 3

        # reset the state, to mock out the case where the first two lines have alread been read in
        processed_logs[log_name] = 2
        stream = StringIO()
        _incremental_print(log_content, processed_logs, log_name, stream)
        # should contain the length of the log (3) - skip previous lines (2) +  no header lines (0)
        assert len(stream.getvalue().splitlines()) == 1
        assert processed_logs[log_name] == 3

    def test_empty_log_is_skipped(self) -> None:
        log_name = "55_log_test"
        log_content = ""
        stream = StringIO()
        processed_logs: Dict[str, int] = {}
        _incremental_print(log_content, processed_logs, log_name, stream)
        # should be empty, no header, no log.
        assert len(stream.getvalue().splitlines()) == 0
        assert processed_logs.get(log_name, None) is None
