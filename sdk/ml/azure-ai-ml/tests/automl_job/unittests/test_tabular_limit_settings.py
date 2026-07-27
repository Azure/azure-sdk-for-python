import pytest

from azure.ai.ml._restclient.arm_ml_service.models import TableVerticalLimitSettings as RestTabularLimitSettings
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
        default_rest = RestTabularLimitSettings(
            enable_early_termination=True,
            exit_score=0.5,
            max_concurrent_trials=10,
            max_cores_per_trial=2,
            max_trials=100,
            timeout="PT10H",
            trial_timeout="PT20M",
        )
        max_nodes_rest = RestTabularLimitSettings(
            enable_early_termination=True,
            exit_score=0.5,
            max_concurrent_trials=10,
            max_cores_per_trial=2,
            max_trials=100,
            timeout="PT10H",
            trial_timeout="PT20M",
        )
        # ``maxNodes`` is preserved via wire-key (dropped from the arm_ml_service model).
        max_nodes_rest["maxNodes"] = 4
        # ``sweepConcurrentTrials``/``sweepTrials`` are preserved via wire-key (default 0) to match
        # the legacy msrest wire.
        default_rest["sweepConcurrentTrials"] = 0
        default_rest["sweepTrials"] = 0
        max_nodes_rest["sweepConcurrentTrials"] = 0
        max_nodes_rest["sweepTrials"] = 0
        rest_objs = {
            "default": default_rest,
            "max_nodes": max_nodes_rest,
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
