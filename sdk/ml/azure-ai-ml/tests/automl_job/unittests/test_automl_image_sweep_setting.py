# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from itertools import product
from typing import Optional

import pytest

from azure.ai.ml._restclient.v2023_04_01_preview.models import BanditPolicy as RestBanditPolicy
from azure.ai.ml._restclient.v2023_04_01_preview.models import EarlyTerminationPolicyType
from azure.ai.ml._restclient.v2023_04_01_preview.models import ImageSweepSettings as RestImageSweepSettings
from azure.ai.ml._restclient.v2023_04_01_preview.models import MedianStoppingPolicy as RestMedianStoppingPolicy
from azure.ai.ml._restclient.v2023_04_01_preview.models import SamplingAlgorithmType
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    TruncationSelectionPolicy as RestTruncationSelectionPolicy,
)
from azure.ai.ml.entities._job.automl.image import ImageSweepSettings
from azure.ai.ml.sweep import BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy


@pytest.mark.unittest
class TestImageSweepSettings:
    _EARLY_TERMINATION_POLICY_OPTIONS = [
        None,
        EarlyTerminationPolicyType.BANDIT,
        EarlyTerminationPolicyType.MEDIAN_STOPPING,
        EarlyTerminationPolicyType.TRUNCATION_SELECTION,
    ]
    _SAMPLING_ALGORITHM_OPTIONS = [
        SamplingAlgorithmType.GRID,
        SamplingAlgorithmType.BAYESIAN,
        SamplingAlgorithmType.RANDOM,
    ]
    _EARLY_TERM_POLICY_AND_SAMPLING_ALG_OPTIONS = list(
        product(_EARLY_TERMINATION_POLICY_OPTIONS, _SAMPLING_ALGORITHM_OPTIONS)
    )

    @pytest.mark.parametrize(
        "early_termination_name,sampling_algorithm_name", _EARLY_TERM_POLICY_AND_SAMPLING_ALG_OPTIONS
    )
    def test_image_sweep_settings_from_rest(
        self,
        early_termination_name: Optional[EarlyTerminationPolicyType],
        sampling_algorithm_name: SamplingAlgorithmType,
    ) -> None:
        image_sweep_settings_rest = self._get_rest_obj(early_termination_name, sampling_algorithm_name)
        expected_image_sweep_settings_obj = self._get_entity_obj(early_termination_name, sampling_algorithm_name)
        image_sweep_settings_obj = ImageSweepSettings._from_rest_object(image_sweep_settings_rest)
        assert (
            image_sweep_settings_obj == expected_image_sweep_settings_obj
        ), f"actual: {image_sweep_settings_obj}, expected: {expected_image_sweep_settings_obj}"

    @pytest.mark.parametrize(
        "early_termination_name,sampling_algorithm_name", _EARLY_TERM_POLICY_AND_SAMPLING_ALG_OPTIONS
    )
    def test_image_sweep_settings_to_rest(
        self,
        early_termination_name: Optional[EarlyTerminationPolicyType],
        sampling_algorithm_name: SamplingAlgorithmType,
    ) -> None:
        image_sweep_settings_obj = self._get_entity_obj(early_termination_name, sampling_algorithm_name)
        expected_image_sweep_settings_rest = self._get_rest_obj(early_termination_name, sampling_algorithm_name)
        image_sweep_settings_rest = image_sweep_settings_obj._to_rest_object()
        assert (
            image_sweep_settings_rest == expected_image_sweep_settings_rest
        ), f"actual: {image_sweep_settings_rest}, expected: {expected_image_sweep_settings_rest}"

    @pytest.mark.parametrize(
        "early_termination_name,sampling_algorithm_name", _EARLY_TERM_POLICY_AND_SAMPLING_ALG_OPTIONS
    )
    def test_equality(
        self,
        early_termination_name: Optional[EarlyTerminationPolicyType],
        sampling_algorithm_name: SamplingAlgorithmType,
    ) -> None:
        image_sweep_settings_obj = self._get_entity_obj(early_termination_name, sampling_algorithm_name)
        # serialize and deserialize to ensure equality
        image_sweep_settings_rest = ImageSweepSettings._to_rest_object(image_sweep_settings_obj)
        image_sweep_settings_obj_2 = ImageSweepSettings._from_rest_object(image_sweep_settings_rest)
        assert (
            image_sweep_settings_obj == image_sweep_settings_obj_2
        ), f"actual: {image_sweep_settings_obj}, expected: {image_sweep_settings_obj_2}"

    def _get_rest_obj(
        self,
        early_termination_name: Optional[EarlyTerminationPolicyType] = None,
        sampling_algorithm_name: SamplingAlgorithmType = SamplingAlgorithmType.GRID,
    ) -> RestImageSweepSettings:
        if early_termination_name == EarlyTerminationPolicyType.BANDIT:
            rest_early_termination_name = RestBanditPolicy(evaluation_interval=10, slack_factor=0.2)
        elif early_termination_name == EarlyTerminationPolicyType.MEDIAN_STOPPING:
            rest_early_termination_name = RestMedianStoppingPolicy(delay_evaluation=5, evaluation_interval=1)
        elif early_termination_name == EarlyTerminationPolicyType.TRUNCATION_SELECTION:
            rest_early_termination_name = RestTruncationSelectionPolicy(
                evaluation_interval=1, truncation_percentage=20, delay_evaluation=5
            )
        else:
            rest_early_termination_name = None

        return RestImageSweepSettings(
            sampling_algorithm=sampling_algorithm_name, early_termination=rest_early_termination_name
        )

    def _get_entity_obj(
        self,
        early_termination_name: Optional[EarlyTerminationPolicyType] = None,
        sampling_algorithm_name: SamplingAlgorithmType = SamplingAlgorithmType.GRID,
    ) -> ImageSweepSettings:
        if early_termination_name == EarlyTerminationPolicyType.BANDIT:
            early_termination_name = BanditPolicy(evaluation_interval=10, slack_factor=0.2)
        elif early_termination_name == EarlyTerminationPolicyType.MEDIAN_STOPPING:
            early_termination_name = MedianStoppingPolicy(delay_evaluation=5, evaluation_interval=1)
        elif early_termination_name == EarlyTerminationPolicyType.TRUNCATION_SELECTION:
            early_termination_name = TruncationSelectionPolicy(
                evaluation_interval=1, truncation_percentage=20, delay_evaluation=5
            )
        else:
            early_termination_name = None

        return ImageSweepSettings(sampling_algorithm=sampling_algorithm_name, early_termination=early_termination_name)
