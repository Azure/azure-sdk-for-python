# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._restclient.arm_ml_service.models import NlpVerticalLimitSettings as RestNlpLimitSettings
from azure.ai.ml._utils.utils import from_iso_duration_format_mins, to_iso_duration_format_mins
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class NlpLimitSettings(RestTranslatableMixin):
    """Limit settings for all AutoML NLP Verticals.

    :keyword max_concurrent_trials: Maximum number of concurrent AutoML iterations.
    :paramtype max_concurrent_trials: int
    :keyword max_trials: Maximum number of AutoML iterations.
    :paramtype max_trials: int
    :keyword timeout_minutes: AutoML job timeout.
    :paramtype timeout_minutes: int

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_automl_nlp.py
                :start-after: [START automl.nlp_limit_settings]
                :end-before: [END automl.nlp_limit_settings]
                :language: python
                :dedent: 8
                :caption: creating an nlp limit settings
    """

    def __init__(
        self,
        *,
        max_concurrent_trials: Optional[int] = None,
        max_trials: int = 1,
        max_nodes: int = 1,
        timeout_minutes: Optional[int] = None,
        trial_timeout_minutes: Optional[int] = None,
    ):
        self.max_concurrent_trials = max_concurrent_trials
        self.max_trials = max_trials
        self.max_nodes = max_nodes
        self.timeout_minutes = timeout_minutes
        self.trial_timeout_minutes = trial_timeout_minutes

    def _to_rest_object(self) -> RestNlpLimitSettings:
        rest_obj = RestNlpLimitSettings(
            max_concurrent_trials=self.max_concurrent_trials,
            max_trials=self.max_trials,
            timeout=to_iso_duration_format_mins(self.timeout_minutes),
        )
        # ``maxNodes``/``trialTimeout`` exist on the 2023-04 wire contract but were dropped from the
        # arm_ml_service (2025-12) model; preserve them via wire-key assignment.
        if self.max_nodes is not None:
            rest_obj["maxNodes"] = self.max_nodes
        trial_timeout = to_iso_duration_format_mins(self.trial_timeout_minutes)
        if trial_timeout is not None:
            rest_obj["trialTimeout"] = trial_timeout
        return rest_obj

    @classmethod
    def _from_rest_object(cls, obj: RestNlpLimitSettings) -> "NlpLimitSettings":
        return cls(
            max_concurrent_trials=obj.max_concurrent_trials,
            max_trials=obj.max_trials,
            max_nodes=obj.get("maxNodes"),
            timeout_minutes=from_iso_duration_format_mins(obj.timeout),
            trial_timeout_minutes=from_iso_duration_format_mins(obj.get("trialTimeout")),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NlpLimitSettings):
            return NotImplemented

        return (
            self.max_concurrent_trials == other.max_concurrent_trials
            and self.max_trials == other.max_trials
            and self.max_nodes == other.max_nodes
            and self.timeout_minutes == other.timeout_minutes
            and self.trial_timeout_minutes == other.trial_timeout_minutes
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
