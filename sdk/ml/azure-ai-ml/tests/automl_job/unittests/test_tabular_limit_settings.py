import pytest
from azure.ai.ml._restclient.v2022_02_01_preview.models import TableVerticalLimitSettings as RestTabularLimitSettings
from azure.ai.ml.entities._job.automl.tabular import TabularLimitSettings


@pytest.mark.unittest
class TestLimitSettings:
    def test_limit_from_rest(self):
        limit_settings_rest = self._get_rest_obj()
        limit_settings_obj = TabularLimitSettings._from_rest_object(limit_settings_rest)
        assert limit_settings_obj == self._get_entity_obj(), "actual: {}, expected: {}".format(
            limit_settings_obj, self._get_entity_obj()
        )

    def test_limit_to_rest(self):
        limit_settings_obj = self._get_entity_obj()
        limit_settings_rest = limit_settings_obj._to_rest_object()
        assert limit_settings_rest == self._get_rest_obj(), "actual: {}, expected: {}".format(
            limit_settings_rest, self._get_rest_obj()
        )

    def test_equality(self):
        limit_settings_obj = self._get_entity_obj()
        # serialize and deserialize to ensure equality
        limit_settings_rest = TabularLimitSettings._to_rest_object(limit_settings_obj)
        limit_settings_obj_2 = TabularLimitSettings._from_rest_object(limit_settings_rest)
        assert limit_settings_obj == limit_settings_obj_2, "actual: {}, expected: {}".format(
            limit_settings_obj, limit_settings_obj_2
        )

    def _get_rest_obj(self):
        return RestTabularLimitSettings(
            enable_early_termination=True,
            exit_score=0.5,
            max_concurrent_trials=10,
            max_cores_per_trial=2,
            max_trials=100,
            timeout="PT10H",
            trial_timeout="PT20M",
        )

    def _get_entity_obj(self):
        return TabularLimitSettings(
            enable_early_termination=True,
            exit_score=0.5,
            max_concurrent_trials=10,
            max_cores_per_trial=2,
            max_trials=100,
            timeout_minutes=600,
            trial_timeout_minutes=20,
        )
