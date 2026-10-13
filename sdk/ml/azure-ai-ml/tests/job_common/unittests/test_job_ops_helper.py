import re
import time
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from io import StringIO
from typing import Dict
from unittest.mock import Mock
from urllib.parse import parse_qs, urlsplit

import pytest
from devtools_testutils.fake_credentials import FakeTokenCredential
from mock import mock_open, patch

from azure.ai.ml._artifacts._artifact_utilities import list_logs_in_datastore
from azure.ai.ml._artifacts._blob_storage_helper import BlobStorageClient
from azure.ai.ml._artifacts._gen2_storage_helper import Gen2StorageClient
from azure.ai.ml._restclient.arm_ml_service.models import DatastoreType, JobBase
from azure.ai.ml._restclient.runhistory.models import RunDetails, RunDetailsWarning
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.exceptions import ValidationException
from azure.ai.ml.operations._job_ops_helper import (
    _get_sorted_filtered_logs,
    _incremental_print,
    get_job_output_uris_from_dataplane,
    has_pat_token,
    list_logs,
    stream_logs_until_completion,
)
from azure.ai.ml.operations._run_operations import RunOperations
from azure.identity import ChainedTokenCredential
from azure.storage.blob import ContainerSasPermissions, generate_container_sas

from .test_vcr_utils import before_record_cb


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
def streaming_job() -> JobBase:
    return JobBase(
        {
            "name": "job-name",
            "properties": {
                "jobType": "Command",
                "properties": {},
                "services": {},
                "outputs": {
                    "default": {
                        "jobOutputType": "uri_folder",
                        "uri": "azureml://datastores/workspaceblobstore/paths/azureml/job-name/",
                    }
                },
            },
        }
    )


@pytest.fixture
def datastore_sas_token(fake_datastore_key: str) -> str:
    return generate_container_sas(
        account_name="teststorage",
        container_name="testcontainer",
        account_key=fake_datastore_key,
        permission=ContainerSasPermissions(read=True, list=True),
        expiry=datetime.now(timezone.utc) + timedelta(hours=1),
    )


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
            # RunHistory reports PascalCase, the ARM contract reports snake_case. Both must resolve.
            ("UriFolder", "MLFlowModel"),
            ("uri_folder", "mlflow_model"),
            ("UriFile", "CustomModel"),
            ("uri_file", "custom_model"),
            ("MLTable", "TritonModel"),
            ("mltable", "triton_model"),
        ],
    )
    def test_get_job_output_uris_from_dataplane_matches_both_type_spellings(self, data_type, model_type) -> None:
        run_outputs = {
            "forecast_data": Mock(asset_id="data-asset-id", type=data_type),
            "trained_model": Mock(asset_id="model-asset-id", type=model_type),
        }
        run_operations = Mock()
        run_operations.get_run_data.return_value.run_metadata.outputs = run_outputs

        dataset_dataplane_operations = Mock()
        dataset_dataplane_operations.get_batch_dataset_uris.return_value.values_property = {
            "data-asset-id": Mock(uri="azureml://datastores/ds/paths/forecast_data")
        }

        model_dataplane_operations = Mock()
        model_dataplane_operations.get_batch_model_uris.return_value.values = {
            "model-asset-id": Mock(path="azureml://datastores/ds/paths/trained_model")
        }

        uris = get_job_output_uris_from_dataplane(
            "job-name",
            run_operations,
            dataset_dataplane_operations,
            model_dataplane_operations,
        )

        dataset_dataplane_operations.get_batch_dataset_uris.assert_called_once_with(["data-asset-id"])
        model_dataplane_operations.get_batch_model_uris.assert_called_once_with(["model-asset-id"])
        assert uris == {
            "forecast_data": "azureml://datastores/ds/paths/forecast_data",
            "trained_model": "azureml://datastores/ds/paths/trained_model",
        }

    @pytest.mark.parametrize(
        "credential_kind,expects_datastore_logs",
        [
            ("account_key", True),
            ("sas_token", False),
            ("sas_with_question_mark", False),
            ("sas_with_empty_signature", False),
            ("identity", False),
            ("missing", False),
            ("empty", False),
        ],
    )
    def test_stream_logs_falls_back_to_run_history_for_unsignable_datastore(
        self,
        credential_kind,
        expects_datastore_logs,
        streaming_job: JobBase,
        fake_datastore_key: str,
        datastore_sas_token: str,
        capsys,
        caplog,
    ) -> None:
        credentials = {
            "account_key": fake_datastore_key,
            "sas_token": datastore_sas_token,
            "sas_with_question_mark": "?" + datastore_sas_token,
            "sas_with_empty_signature": "sp=rl&sig=",
            "identity": ChainedTokenCredential(FakeTokenCredential()),
            "missing": None,
            "empty": "",
        }
        log_name = "user_logs/std_log.txt"
        run_history_url = "https://test.invalid/run-history/log"
        datastore_url = "https://test.invalid/datastore/log"
        run_operations = Mock()
        run_operations.get_run_details.side_effect = [
            RunDetails(status="Running", log_files={}),
            RunDetails(status="Running", log_files={log_name: run_history_url}),
            RunDetails(status="Completed", log_files={log_name: run_history_url}),
        ]
        requests_pipeline = Mock()
        requests_pipeline.with_policies.return_value = requests_pipeline
        requests_pipeline.get.side_effect = [
            Mock(status_code=200, text=Mock(return_value="first line\n")),
            Mock(status_code=200, text=Mock(return_value="first line\nsecond line\n")),
        ]

        ds_info = {"credential": credentials[credential_kind], "storage_type": DatastoreType.AZURE_BLOB}
        caplog.set_level("DEBUG", logger="azure.ai.ml.operations._job_ops_helper")

        with patch("azure.ai.ml.operations._job_ops_helper.get_datastore_info", return_value=ds_info), patch(
            "azure.ai.ml.operations._job_ops_helper.list_logs_in_datastore",
            return_value={log_name: datastore_url},
        ) as mock_list_logs_in_datastore, patch("azure.ai.ml.operations._job_ops_helper.time.sleep"):
            stream_logs_until_completion(
                run_operations,
                streaming_job,
                datastore_operations=Mock(),
                requests_pipeline=requests_pipeline,
            )

        assert mock_list_logs_in_datastore.called is expects_datastore_logs
        expected_url = datastore_url if expects_datastore_logs else run_history_url
        assert [call.args[0] for call in requests_pipeline.get.call_args_list] == [expected_url, expected_url]
        output = capsys.readouterr().out
        assert output.count("\nfirst line\n") == 1
        assert output.count("\nsecond line\n") == 1
        assert "Execution Summary" in output
        assert fake_datastore_key not in output + caplog.text
        assert datastore_sas_token not in output + caplog.text

    @pytest.mark.parametrize(
        "storage_type,storage_class,endpoint",
        [
            (DatastoreType.AZURE_BLOB, BlobStorageClient, "blob"),
            (DatastoreType.AZURE_DATA_LAKE_GEN2, Gen2StorageClient, "dfs"),
        ],
    )
    @pytest.mark.parametrize("path", ["azureml/job-name", "azureml/job-name/"])
    @pytest.mark.parametrize("long_uri", [False, True])
    @pytest.mark.parametrize("log_name", ["user_logs/std_log.txt", "azureml-logs/70_driver_log.txt"])
    def test_stream_logs_from_key_datastore_uses_storage_path(
        self, storage_type, storage_class, endpoint, path, long_uri, log_name, streaming_job, fake_datastore_key, capsys
    ) -> None:
        uri_prefix = "azureml://subscriptions/sub/resourcegroups/rg/workspaces/ws/" if long_uri else "azureml://"
        streaming_job.properties.outputs["default"].uri = f"{uri_prefix}datastores/workspaceblobstore/paths/{path}"
        blob_prefix = "azureml/job-name/"
        item_name = blob_prefix + log_name
        storage_client = Mock(spec=storage_class)
        storage_client.list.side_effect = lambda starts_with: [item_name] if item_name.startswith(starts_with) else []
        ds_info = {
            "storage_type": storage_type,
            "storage_account": "teststorage",
            "account_url": f"https://teststorage.{endpoint}.core.windows.net",
            "container_name": "testcontainer",
            "credential": fake_datastore_key,
        }
        run_operations = Mock()
        run_operations.get_run_details.side_effect = [
            RunDetails(status="Running", log_files={}),
            RunDetails(status="Completed", log_files={}),
        ]
        requests_pipeline = Mock()
        requests_pipeline.with_policies.return_value = requests_pipeline
        requests_pipeline.get.return_value = Mock(status_code=200, text=Mock(return_value="datastore log\n"))

        with patch("azure.ai.ml.operations._job_ops_helper.get_datastore_info", return_value=ds_info), patch(
            "azure.ai.ml._artifacts._artifact_utilities.get_storage_client", return_value=storage_client
        ), patch("azure.ai.ml.operations._job_ops_helper.time.sleep"):
            stream_logs_until_completion(
                run_operations, streaming_job, datastore_operations=Mock(), requests_pipeline=requests_pipeline
            )

        assert [call.kwargs["starts_with"] for call in storage_client.list.call_args_list] == [
            blob_prefix + "user_logs/",
            blob_prefix + "azureml-logs/",
        ]
        requests_pipeline.get.assert_called_once()
        log_url = urlsplit(requests_pipeline.get.call_args.args[0])
        assert log_url.netloc == f"teststorage.{endpoint}.core.windows.net"
        assert log_url.path == f"/testcontainer/{item_name}"
        assert parse_qs(log_url.query)["sp"] == ["r"]
        assert parse_qs(log_url.query)["sig"]
        assert "\ndatastore log\n" in capsys.readouterr().out

    @pytest.mark.parametrize(
        "uri",
        [
            "azureml://datastores/workspaceblobstore/paths/",
            "azureml://subscriptions/sub/resourcegroups/rg/workspaces/ws/datastores/workspaceblobstore/paths/",
        ],
    )
    def test_stream_logs_rejects_empty_datastore_path(self, uri, streaming_job) -> None:
        streaming_job.properties.outputs["default"].uri = uri
        datastore_operations = Mock()
        with pytest.raises(ValidationException, match="Invalid AzureML datastore path URI"):
            stream_logs_until_completion(
                Mock(), streaming_job, datastore_operations=datastore_operations, requests_pipeline=Mock()
            )
        datastore_operations.get.assert_not_called()

    @pytest.mark.parametrize(
        "storage_type,storage_class",
        [
            (DatastoreType.AZURE_BLOB, BlobStorageClient),
            (DatastoreType.AZURE_DATA_LAKE_GEN2, Gen2StorageClient),
        ],
    )
    def test_list_logs_in_datastore_with_empty_prefix(self, storage_type, storage_class, fake_datastore_key) -> None:
        log_name = "user_logs/std_log.txt"
        storage_client = Mock(spec=storage_class)
        storage_client.list.side_effect = [[log_name], []]
        ds_info = {
            "storage_type": storage_type,
            "storage_account": "teststorage",
            "account_url": "https://teststorage.blob.core.windows.net",
            "container_name": "testcontainer",
            "credential": fake_datastore_key,
        }

        with patch("azure.ai.ml._artifacts._artifact_utilities.get_storage_client", return_value=storage_client):
            logs = list_logs_in_datastore(ds_info, prefix="", legacy_log_folder_name="/azureml-logs/")

        assert [call.kwargs["starts_with"] for call in storage_client.list.call_args_list] == [
            "user_logs/",
            "azureml-logs/",
        ]
        assert set(logs) == {log_name}
        assert urlsplit(logs[log_name]).path == f"/testcontainer/{log_name}"


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
