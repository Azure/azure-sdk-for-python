# coding=utf-8
# Copyright 2024 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Portions Copyright (c) Microsoft Corporation

"""Library for scoring and evaluation of text samples.

Aggregation functions use bootstrap resampling to compute confidence intervals
as per the original ROUGE perl implementation.
"""

import abc
import collections
from typing import Dict


class Score(collections.namedtuple("Score", ["precision", "recall", "fmeasure"])):
    """Tuple containing precision, recall, and f-measure values."""


class BaseScorer(object, metaclass=abc.ABCMeta):
    """Base class for Scorer objects."""

    @abc.abstractmethod
    def score(self, target, prediction):
        """Calculates score between the target and prediction.

        Args:
          target: Text containing the target (ground truth) text.
          prediction: Text containing the predicted text.

        Returns:
          A dict mapping each score_type (string) to Score object.
        """


class AggregateScore(collections.namedtuple("AggregateScore", ["low", "mid", "high"])):
    """Tuple containing confidence intervals for scores."""


def fmeasure(precision, recall):
    """Computes f-measure given precision and recall values."""

    if precision + recall > 0:
        return 2 * precision * recall / (precision + recall)
    else:
        return 0.0
