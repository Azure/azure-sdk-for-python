from typing import Callable

import pydash
import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient
from azure.ai.ml.constants._common import LROConfigurations
from azure.ai.ml.entities import AmlTokenConfiguration, CronTrigger, PipelineJob
from azure.ai.ml.entities._load_functions import load_job, load_schedule

from .._util import _SCHEDULE_TIMEOUT_SECOND, TRIGGER_ENDTIME, TRIGGER_ENDTIME_DICT


@pytest.mark.timeout(_SCHEDULE_TIMEOUT_SECOND)
@pytest.mark.e2etest
@pytest.mark.usefixtures(
    "recorded_test", "mock_code_hash", "mock_asset_name", "mock_component_hash", "mock_anon_component_version"
)
@pytest.mark.pipeline_test
class TestSchedule(AzureRecordedTestCase):
    def test_schedule_lifetime(self, client: MLClient, randstr: Callable[[], str]):
        params_override = [{"name": randstr("name")}]
        params_override.extend(TRIGGER_ENDTIME_DICT)
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_file_reference.yml"
        schedule = load_schedule(test_path, params_override=params_override)
        # create
        rest_schedule = client.schedules.begin_create_or_update(schedule).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )
        assert rest_schedule._is_enabled is True
        # list
        rest_schedule_list = [item for item in client.schedules.list()]
        assert rest_schedule_list != []
        # update
        schedule.create_job.experiment_name = "test_schedule_exp"
        schedule.create_job.identity = AmlTokenConfiguration()
        rest_schedule = client.schedules.begin_create_or_update(schedule).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )
        assert rest_schedule._is_enabled is True
        job: PipelineJob = rest_schedule.create_job
        assert isinstance(job.identity, AmlTokenConfiguration)
        # disable
        rest_schedule = client.schedules.begin_disable(schedule.name).result(timeout=LROConfigurations.POLLING_TIMEOUT)
        assert rest_schedule._is_enabled is False
        # enable
        rest_schedule = client.schedules.begin_enable(schedule.name).result(timeout=LROConfigurations.POLLING_TIMEOUT)
        assert rest_schedule._is_enabled is True
        # invalid delete
        with pytest.raises(Exception) as e:
            client.schedules.begin_delete(schedule.name).result(timeout=LROConfigurations.POLLING_TIMEOUT)
        assert "Cannot delete an active trigger" in str(e)
        # delete
        rest_schedule = client.schedules.begin_disable(schedule.name).result(timeout=LROConfigurations.POLLING_TIMEOUT)
        client.schedules.begin_delete(rest_schedule.name).result(timeout=LROConfigurations.POLLING_TIMEOUT)
        with pytest.raises(Exception) as e:
            client.schedules.get(schedule.name)
        assert "not found" in str(e)

    def test_load_cron_schedule_with_job_updates(self, client: MLClient, randstr: Callable[[], str]):
        params_override = [{"name": randstr("name")}]
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_job_updates.yml"
        schedule = load_schedule(test_path, params_override=[*TRIGGER_ENDTIME_DICT, *params_override])
        rest_schedule = client.schedules.begin_create_or_update(schedule).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )
        assert rest_schedule.name == schedule.name
        client.schedules.begin_disable(schedule.name)
        # assert updates
        job: PipelineJob = rest_schedule.create_job
        assert isinstance(job.identity, AmlTokenConfiguration)
        assert job.inputs["hello_string_top_level_input"]._data == "${{creation_context.trigger_time}}"

    @pytest.mark.usefixtures("mock_set_headers_with_user_aml_token")
    def test_load_cron_schedule_with_arm_id(self, client: MLClient, randstr: Callable[[], str]):
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_inline_comps.yml",
            params_override=params_override,
        )
        pipeline_job = client.jobs.create_or_update(pipeline_job)
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_arm_id.yml"
        params_override = [{"create_job": "azureml:%s" % pipeline_job.id}]
        schedule = load_schedule(test_path, params_override=params_override)
        rest_schedule = client.schedules.begin_create_or_update(schedule).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )
        assert rest_schedule.name == schedule.name
        # Asset the empty string added by sdk
        assert rest_schedule.create_job.experiment_name == ""
        client.schedules.begin_disable(schedule.name)
        assert rest_schedule.create_job.id is not None
        # Set to None to align with yaml as service will fill this
        rest_schedule.trigger.start_time = None
        assert (
            pydash.omit(rest_schedule.trigger._to_rest_object().as_dict(), "start_time")
            == CronTrigger(time_zone="UTC", expression="15 10 * * 1")._to_rest_object().as_dict()
        )

    @pytest.mark.usefixtures("mock_set_headers_with_user_aml_token")
    def test_load_cron_schedule_with_arm_id_and_updates(self, client: MLClient, randstr: Callable[[], str]):
        params_override = [{"name": randstr("name")}]
        test_job_path = "./tests/test_configs/pipeline_jobs/hello-pipeline-abc.yml"
        pipeline_job = load_job(
            test_job_path,
            params_override=params_override,
        )
        pipeline_job = client.jobs.create_or_update(pipeline_job)
        params_override = [{"create_job": "azureml:%s" % pipeline_job.id}]
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_arm_id_and_updates.yml"
        schedule = load_schedule(test_path, params_override=params_override)
        rest_schedule = client.schedules.begin_create_or_update(schedule).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )
        assert rest_schedule.name == schedule.name
        client.schedules.begin_disable(schedule.name)
        assert (
            rest_schedule.trigger._to_rest_object()
            == CronTrigger(
                start_time="2022-03-10 10:15:00", time_zone="UTC", expression="15 10 * * 1"
            )._to_rest_object()
        )
        # TODO: add job assertion after supported
        # assert rest_schedule.create_job.id == pipeline_job.id
        # assert rest_schedule.create_job.inputs["hello_string_top_level_input"] == "${{name}}"
        # assert rest_schedule.create_job.settings.continue_on_step_failure is True

    @pytest.mark.usefixtures("snapshot_hash_sanitizer")
    def test_load_recurrence_schedule_no_pattern(self, client: MLClient, randstr: Callable[[], str]):
        params_override = [{"name": randstr("name")}]
        test_path = "./tests/test_configs/schedule/hello_recurrence_schedule_no_pattern.yml"
        schedule = load_schedule(test_path, params_override=[*TRIGGER_ENDTIME_DICT, *params_override])
        rest_schedule = client.schedules.begin_create_or_update(schedule).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )
        assert rest_schedule.name == schedule.name
        client.schedules.begin_disable(schedule.name)
        assert rest_schedule.trigger._to_rest_object().as_dict() == {
            "end_time": TRIGGER_ENDTIME,
            "start_time": "2022-05-10 10:15:00",
            "time_zone": "Pacific Standard Time",
            "trigger_type": "Recurrence",
            "frequency": "day",
            "interval": 1,
            "schedule": {"hours": [], "minutes": []},
        }

    @pytest.mark.usefixtures("snapshot_hash_sanitizer")
    def test_load_recurrence_schedule_with_pattern(self, client: MLClient, randstr: Callable[[], str]):
        params_override = [{"name": randstr("name")}]
        test_path = "./tests/test_configs/schedule/hello_recurrence_schedule_with_pattern.yml"
        schedule = load_schedule(test_path, params_override=params_override)
        rest_schedule = client.schedules.begin_create_or_update(schedule).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )
        assert rest_schedule.name == schedule.name
        client.schedules.begin_disable(schedule.name)
        assert rest_schedule.trigger._to_rest_object().as_dict() == {
            "start_time": "2022-05-10 10:15:00",
            "time_zone": "Pacific Standard Time",
            "trigger_type": "Recurrence",
            "frequency": "week",
            "interval": 1,
            "schedule": {"hours": [10], "minutes": [15], "week_days": ["Monday"]},
        }

    def test_create_schedule_pipeline_with_output_binding(self, client: MLClient, randstr: Callable[[], str]):
        params_override = [{"name": randstr("name")}]
        test_path = "./tests/test_configs/schedule/schedule_pipeline_with_output_binding.yml"
        schedule = load_schedule(test_path, params_override=params_override)
        rest_schedule = client.schedules.begin_create_or_update(schedule).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )
        assert rest_schedule.name == schedule.name
        rest_job = rest_schedule.create_job._to_dict()
        assert rest_job["inputs"] == {
            "int_param": "10",
            "data_input": {
                "mode": "ro_mount",
                "type": "uri_file",
                "path": "azureml:https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
            },
        }
        assert rest_job["outputs"] == {
            "output1": {"mode": "rw_mount", "type": "uri_folder"},
            "output2": {"mode": "rw_mount", "type": "uri_folder"},
            "output3": {"mode": "rw_mount", "type": "uri_folder"},
        }

    @pytest.mark.usefixtures(
        "enable_pipeline_private_preview_features",
    )
    def test_command_job_schedule(self, client: MLClient, randstr: Callable[[], str]):
        params_override = [{"name": randstr("name")}]
        test_path = "./tests/test_configs/schedule/local_cron_command_job.yml"
        schedule = load_schedule(test_path, params_override=params_override)
        rest_schedule = client.schedules.begin_create_or_update(schedule).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )
        assert rest_schedule.name == schedule.name
        client.schedules.begin_disable(schedule.name)
        rest_schedule_job_dict = rest_schedule._to_dict()["create_job"]
        # pop added status, default resources, empty services from rest dict
        rest_schedule_job_dict.pop("status", None)
        rest_schedule_job_dict.pop("services", None)
        rest_schedule_job_dict.pop("resources", None)
        schedule_job_dict = schedule._to_dict()["create_job"]
        # pop job name, empty parameters from local dict
        schedule_job_dict.pop("parameters", None)
        schedule_job_dict.pop("name", None)
        # add default mode for local
        schedule_job_dict["inputs"]["hello_input"]["mode"] = "ro_mount"
        assert schedule_job_dict == rest_schedule_job_dict

    @pytest.mark.skipif(
        condition=not is_live(),
        reason="TODO (2374610): hash sanitizer is being applied unnecessarily and forcing playback failures",
    )
    @pytest.mark.usefixtures(
        "enable_pipeline_private_preview_features",
    )
    def test_spark_job_schedule(self, client: MLClient, randstr: Callable[[], str]):
        params_override = [{"name": randstr("name")}]
        test_path = "./tests/test_configs/schedule/local_cron_spark_job.yml"
        schedule = load_schedule(test_path, params_override=params_override)
        rest_schedule = client.schedules.begin_create_or_update(schedule).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )
        assert rest_schedule.name == schedule.name
        client.schedules.begin_disable(schedule.name)
        rest_schedule_job_dict = rest_schedule._to_dict()["create_job"]
        # pop added experiment name Default
        rest_schedule_job_dict.pop("experiment_name", None)
        rest_schedule_job_dict.pop("status", None)
        schedule_job_dict = schedule._to_dict()["create_job"]
        # pop job name, empty parameters from local dict
        assert schedule_job_dict == rest_schedule_job_dict
