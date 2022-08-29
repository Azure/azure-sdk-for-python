import pytest
from marshmallow import ValidationError

from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.entities._load_functions import load_schedule

from .._util import _SCHEDULE_TIMEOUT_SECOND


@pytest.mark.timeout(_SCHEDULE_TIMEOUT_SECOND)
@pytest.mark.unittest
class TestScheduleSchema:
    def test_load_cron_schedule_with_file_reference(self):
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_file_reference.yml"
        schedule = load_schedule(test_path)
        expected_dict = {
            "name": "weekly_retrain_2022_cron_file",
            "description": "a weekly retrain schedule",
            "tags": {},
            "display_name": "weekly retrain schedule",
            "trigger": {
                "start_time": "2022-03-10T10:15:00",
                "end_time": "2022-06-10T10:15:00",
                "time_zone": "Pacific Standard Time",
                "type": "cron",
                "expression": "15 10 * * 1",
            },
            "create_job": {
                "tags": {},
                "display_name": "hello_pipeline_abc",
                "properties": {},
                "compute": "azureml:cpu-cluster",
                "type": "pipeline",
                "settings": {},
                "inputs": {"hello_string_top_level_input": {"path": "${{name}}"}},
                "outputs": {},
                "jobs": {
                    "a": {
                        "$schema": "{}",
                        "command": "echo hello ${{inputs.hello_string}}",
                        "environment_variables": {},
                        "inputs": {"hello_string": {"path": "${{parent.inputs.hello_string_top_level_input}}"}},
                        "outputs": {},
                        "component": {
                            "name": "azureml_anonymous",
                            "tags": {},
                            "version": "1",
                            "is_deterministic": True,
                            "inputs": {"hello_string": {"type": "string"}},
                            "outputs": {},
                            "type": "command",
                            "command": "echo hello ${{inputs.hello_string}}",
                            "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu@latest",
                        },
                        "type": "command",
                    },
                    "b": {
                        "$schema": "{}",
                        "command": 'echo "world" >> ${{outputs.world_output}}/world.txt',
                        "environment_variables": {},
                        "inputs": {},
                        "outputs": {},
                        "component": {
                            "name": "azureml_anonymous",
                            "tags": {},
                            "version": "1",
                            "is_deterministic": True,
                            "inputs": {},
                            "outputs": {"world_output": {"type": "uri_folder"}},
                            "type": "command",
                            "command": 'echo "world" >> ${{outputs.world_output}}/world.txt',
                            "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu@latest",
                        },
                        "type": "command",
                    },
                    "c": {
                        "$schema": "{}",
                        "command": "echo ${{inputs.world_input}}/world.txt",
                        "environment_variables": {},
                        "inputs": {"world_input": {"path": "${{parent.jobs.b.outputs.world_output}}"}},
                        "outputs": {},
                        "component": {
                            "name": "azureml_anonymous",
                            "tags": {},
                            "version": "1",
                            "is_deterministic": True,
                            "inputs": {"world_input": {"type": "uri_folder"}},
                            "outputs": {},
                            "type": "command",
                            "command": "echo ${{inputs.world_input}}/world.txt",
                            "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu@latest",
                        },
                        "type": "command",
                    },
                },
            },
        }
        assert schedule._to_dict() == expected_dict

    def test_load_cron_schedule_with_job_updates(self):
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_job_updates.yml"
        yaml_obj = load_yaml(test_path)
        expected_updates = yaml_obj["create_job"]
        expected_updates.pop("job")
        # Workaround the binding shape changes
        expected_updates["inputs"]["hello_string_top_level_input"] = {"path": "${{creation_context.trigger_time}}"}
        scheduled_job = load_schedule(test_path).create_job
        actual_dict = scheduled_job._to_dict()
        for key, val in expected_updates.items():
            assert actual_dict[key] == val

    def test_load_cron_schedule_with_arm_id(self):
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_arm_id.yml"
        schedule = load_schedule(test_path)
        expected_dict = {
            "name": "weekly_retrain_2022_cron_arm",
            "description": "a weekly retrain schedule",
            "tags": {},
            "display_name": "weekly retrain schedule",
            "trigger": {"time_zone": "UTC", "type": "cron", "expression": "15 10 * * 1"},
            "create_job": "azureml:/subscriptions/d511f82f-71ba-49a4-8233-d7be8a3650f4/resourceGroups/RLTesting/providers/Microsoft.MachineLearningServices/workspaces/AnkitWS/jobs/test_617704734544",
        }
        assert schedule._to_dict() == expected_dict

    def test_load_cron_schedule_with_arm_id_and_updates(self):
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_arm_id_and_updates.yml"
        schedule = load_schedule(test_path)
        expected_dict = {
            "create_job": {
                "experiment_name": "schedule_test_exp",
                "id": "azureml:/subscriptions/d511f82f-71ba-49a4-8233-d7be8a3650f4/resourceGroups/RLTesting/providers/Microsoft.MachineLearningServices/workspaces/AnkitWS/jobs/test_617704734544",
                "inputs": {"hello_string_top_level_input": {"path": "${{name}}"}},
                "jobs": {},
                "outputs": {},
                "properties": {},
                "settings": {"continue_on_step_failure": True, "default_compute": "azureml:cpu-cluster"},
                "tags": {},
                "type": "pipeline",
            },
            "name": "weekly_retrain_2022_cron_arm_updates",
            "tags": {},
            "trigger": {
                "expression": "15 10 * * 1",
                "start_time": "2022-03-10T10:15:00",
                "time_zone": "UTC",
                "type": "cron",
            },
        }
        assert schedule._to_dict() == expected_dict

    def test_load_recurrence_schedule_no_pattern(self):
        test_path = "./tests/test_configs/schedule/hello_recurrence_schedule_no_pattern.yml"
        schedule = load_schedule(test_path)
        yaml_obj = load_yaml(test_path)
        expected_trigger_dict = yaml_obj["trigger"]
        # Append empty pattern
        expected_trigger_dict["schedule"] = {"hours": [], "minutes": []}
        assert schedule._to_dict()["trigger"] == expected_trigger_dict

    def test_load_recurrence_schedule_with_pattern(self):
        test_path = "./tests/test_configs/schedule/hello_recurrence_schedule_with_pattern.yml"
        schedule = load_schedule(test_path)
        yaml_obj = load_yaml(test_path)
        expected_trigger_dict = {
            "frequency": "week",
            "interval": 1,
            "schedule": {"hours": [10], "minutes": [15], "week_days": ["monday"]},
            "start_time": "2022-05-10T10:15:00",
            "time_zone": "Pacific Standard Time",
            "type": "recurrence",
        }
        assert schedule._to_dict()["trigger"] == expected_trigger_dict
        expected_updates = yaml_obj["create_job"]
        expected_updates.pop("job")
        scheduled_job = load_schedule(test_path).create_job
        actual_dict = scheduled_job._to_dict()
        for key, val in expected_updates.items():
            assert actual_dict[key] == val

    def test_load_invalid_schedule_missing_type(self):
        test_path = "./tests/test_configs/schedule/invalid/hello_cron_schedule_with_arm_id_no_type.yml"
        with pytest.raises(ValidationError) as e:
            load_schedule(test_path)
        assert "'type' must be specified when scheduling a remote job with updates." in e.value.messages[0]
