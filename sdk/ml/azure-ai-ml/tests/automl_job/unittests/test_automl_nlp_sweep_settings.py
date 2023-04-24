from itertools import product
from typing import Optional

import pytest

from azure.ai.ml._restclient.v2023_04_01_preview.models import BanditPolicy as RestBanditPolicy
from azure.ai.ml._restclient.v2023_04_01_preview.models import EarlyTerminationPolicyType
from azure.ai.ml._restclient.v2023_04_01_preview.models import MedianStoppingPolicy as RestMedianStoppingPolicy
from azure.ai.ml._restclient.v2023_04_01_preview.models import NlpSweepSettings as RestNlpSweepSettings
from azure.ai.ml._restclient.v2023_04_01_preview.models import SamplingAlgorithmType
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    TruncationSelectionPolicy as RestTruncationSelectionPolicy,
)
from azure.ai.ml.automl import NlpSweepSettings
from azure.ai.ml.sweep import BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy


class TestNlpSweepSettings:
    ALL_TERMINATION_POLICIES = [
        None,
        EarlyTerminationPolicyType.BANDIT,
        EarlyTerminationPolicyType.MEDIAN_STOPPING,
        EarlyTerminationPolicyType.TRUNCATION_SELECTION,
    ]

    ALL_SAMPLING_ALGORITHMS = [
        SamplingAlgorithmType.GRID,
        SamplingAlgorithmType.BAYESIAN,
        SamplingAlgorithmType.RANDOM,
    ]

    EARLY_TERM_SAMPL_ALG_PAIRS = list(product(ALL_TERMINATION_POLICIES, ALL_SAMPLING_ALGORITHMS))

    @pytest.mark.parametrize("early_termination_name,sampling_algorithm_name", EARLY_TERM_SAMPL_ALG_PAIRS)
    def test_nlp_sweep_settings_from_rest(
        self,
        early_termination_name: Optional[EarlyTerminationPolicyType],
        sampling_algorithm_name: SamplingAlgorithmType,
    ) -> None:
        nlp_sweep_settings_rest = self._get_rest_obj(early_termination_name, sampling_algorithm_name)
        expected_nlp_sweep_settings_obj = self._get_entity_obj(early_termination_name, sampling_algorithm_name)
        nlp_sweep_settings_obj = NlpSweepSettings._from_rest_object(nlp_sweep_settings_rest)
        assert (
            nlp_sweep_settings_obj == expected_nlp_sweep_settings_obj
        ), f"expected: {expected_nlp_sweep_settings_obj}, actual: {nlp_sweep_settings_obj}"

    @pytest.mark.parametrize("early_termination_name,sampling_algorithm_name", EARLY_TERM_SAMPL_ALG_PAIRS)
    def test_nlp_sweep_settings_to_rest(
        self,
        early_termination_name: Optional[EarlyTerminationPolicyType],
        sampling_algorithm_name: SamplingAlgorithmType,
    ) -> None:
        expected_nlp_sweep_settings_rest = self._get_rest_obj(early_termination_name, sampling_algorithm_name)
        nlp_sweep_settings_obj = self._get_entity_obj(early_termination_name, sampling_algorithm_name)
        nlp_sweep_settings_rest = nlp_sweep_settings_obj._to_rest_object()
        assert (
            nlp_sweep_settings_rest == expected_nlp_sweep_settings_rest
        ), f"expected: {expected_nlp_sweep_settings_rest}, actual: {nlp_sweep_settings_rest}"

    @pytest.mark.parametrize("early_termination_name,sampling_algorithm_name", EARLY_TERM_SAMPL_ALG_PAIRS)
    def test_nlp_sweep_settings_round_trip(
        self,
        early_termination_name: Optional[EarlyTerminationPolicyType],
        sampling_algorithm_name: SamplingAlgorithmType,
    ) -> None:
        expected_nlp_sweep_settings_obj = self._get_entity_obj(early_termination_name, sampling_algorithm_name)
        rest_sweep_settings_obj = expected_nlp_sweep_settings_obj._to_rest_object()
        round_trip_nlp_sweep_settings_obj = NlpSweepSettings._from_rest_object(rest_sweep_settings_obj)
        assert (
            round_trip_nlp_sweep_settings_obj == expected_nlp_sweep_settings_obj
        ), f"expected: {expected_nlp_sweep_settings_obj}, actual: {round_trip_nlp_sweep_settings_obj}"

    def _get_entity_obj(
        self,
        early_termination_name: Optional[EarlyTerminationPolicyType],
        sampling_algorithm_name: SamplingAlgorithmType = SamplingAlgorithmType.GRID,
    ) -> NlpSweepSettings:
        early_termination_policy = None
        if early_termination_name == EarlyTerminationPolicyType.BANDIT:
            early_termination_policy = BanditPolicy(evaluation_interval=10, slack_factor=0.2)
        elif early_termination_name == EarlyTerminationPolicyType.MEDIAN_STOPPING:
            early_termination_policy = MedianStoppingPolicy(delay_evaluation=5, evaluation_interval=1)
        elif early_termination_name == EarlyTerminationPolicyType.TRUNCATION_SELECTION:
            early_termination_policy = TruncationSelectionPolicy(
                evaluation_interval=1, truncation_percentage=20, delay_evaluation=5
            )
        return NlpSweepSettings(early_termination=early_termination_policy, sampling_algorithm=sampling_algorithm_name)

    def _get_rest_obj(
        self,
        early_termination_name: Optional[EarlyTerminationPolicyType] = None,
        sampling_algorithm_name: SamplingAlgorithmType = SamplingAlgorithmType.GRID,
    ) -> RestNlpSweepSettings:
        early_termination_policy = None
        if early_termination_name == EarlyTerminationPolicyType.BANDIT:
            early_termination_policy = RestBanditPolicy(evaluation_interval=10, slack_factor=0.2)
        elif early_termination_name == EarlyTerminationPolicyType.MEDIAN_STOPPING:
            early_termination_policy = RestMedianStoppingPolicy(delay_evaluation=5, evaluation_interval=1)
        elif early_termination_name == EarlyTerminationPolicyType.TRUNCATION_SELECTION:
            early_termination_policy = RestTruncationSelectionPolicy(
                evaluation_interval=1, truncation_percentage=20, delay_evaluation=5
            )
        return RestNlpSweepSettings(
            sampling_algorithm=sampling_algorithm_name, early_termination=early_termination_policy
        )
