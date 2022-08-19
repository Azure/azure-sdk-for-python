# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import unittest
import pytest
import logging

from azure.ai.ml.sweep import BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy
from msrest.serialization import _LOGGER


@pytest.mark.unittest
class TestAutoMLImageSweepSettings(unittest.TestCase):
    def test_early_termination_not_a_known_attribute_error(self):
        with self.assertLogs(_LOGGER, level=logging.WARNING) as logger:
            # create an instance of BanditPolicy/MedianStoppingPolicy/TrucationSelectionPolicy.
            # validate in logs we dont have "is not a known attribute of class" error.
            BanditPolicy(evaluation_interval=10, slack_factor=0.2)
            MedianStoppingPolicy(delay_evaluation=10, evaluation_interval=1)
            TruncationSelectionPolicy(delay_evaluation=10, evaluation_interval=1)
            for log in logger.output:
                assert "is not a known attribute of class" not in log

            # create Bandit policy and pass `type` attribute which would raise warning.
            BanditPolicy(evaluation_interval=10, slack_factor=0.2, type="bandit")
            for log in logger.output:
                assert "is not a known attribute of class" in log
