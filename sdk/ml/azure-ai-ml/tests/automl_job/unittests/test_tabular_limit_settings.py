import pytest

from azure.ai.ml._restclient.v2023_04_01_preview.models import TableVerticalLimitSettings as RestTabularLimitSettings
from azure.ai.ml.entities._job.automl.tabular import TabularLimitSettings


@pytest.mark.automl_test
@pytest.mark.unittest
class TestLimitSettings:
    @pytest.mark.parametrize(
        "scenario",
        [
            "default",
            "max_nodes",
        ],
    )
    def test_limit_from_rest(self, scenario):
        limit_settings_rest = self._get_rest_obj(scenario)
        limit_settings_obj = TabularLimitSettings._from_rest_object(limit_settings_rest)
        assert limit_settings_obj == self._get_entity_obj(scenario), "actual: {}, expected: {}".format(
            limit_settings_obj, self._get_entity_obj(scenario)
        )

    @pytest.mark.parametrize(
        "scenario",
        [
            "default",
            "max_nodes",
        ],
    )
    def test_limit_to_rest(self, scenario):
        limit_settings_obj = self._get_entity_obj(scenario)
        limit_settings_rest = limit_settings_obj._to_rest_object()
        assert limit_settings_rest == self._get_rest_obj(scenario), "actual: {}, expected: {}".format(
            limit_settings_rest, self._get_rest_obj(scenario)
        )

    @pytest.mark.parametrize(
        "scenario",
        [
            "default",
            "max_nodes",
        ],
    )
    def test_equality(self, scenario):
        limit_settings_obj = self._get_entity_obj(scenario)
        # serialize and deserialize to ensure equality
        limit_settings_rest = TabularLimitSettings._to_rest_object(limit_settings_obj)
        limit_settings_obj_2 = TabularLimitSettings._from_rest_object(limit_settings_rest)
        assert limit_settings_obj == limit_settings_obj_2, "actual: {}, expected: {}".format(
            limit_settings_obj, limit_settings_obj_2
        )

    def _get_rest_obj(self, scenario):
        rest_objs = {
            "default": RestTabularLimitSettings(
                enable_early_termination=True,
                exit_score=0.5,
                max_concurrent_trials=10,
                max_cores_per_trial=2,
                max_trials=100,
                timeout="PT10H",
                trial_timeout="PT20M",
                max_nodes=None,
            ),
            "max_nodes": RestTabularLimitSettings(
                enable_early_termination=True,
                exit_score=0.5,
                max_concurrent_trials=10,
                max_cores_per_trial=2,
                max_trials=100,
                timeout="PT10H",
                trial_timeout="PT20M",
                max_nodes=4,
            ),
        }
        return rest_objs[scenario]

    def _get_entity_obj(self, scenario):
        entity_objs = {
            "default": TabularLimitSettings(
                enable_early_termination=True,
                exit_score=0.5,
                max_concurrent_trials=10,
                max_cores_per_trial=2,
                max_trials=100,
                timeout_minutes=600,
                trial_timeout_minutes=20,
                max_nodes=None,
            ),
            "max_nodes": TabularLimitSettings(
                enable_early_termination=True,
                exit_score=0.5,
                max_concurrent_trials=10,
                max_cores_per_trial=2,
                max_trials=100,
                timeout_minutes=600,
                trial_timeout_minutes=20,
                max_nodes=4,
            ),
        }
        return entity_objs[scenario]
