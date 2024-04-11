# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional

from azure.ai.ml._restclient.v2023_08_01_preview.models import Objective as RestObjective
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class Objective(RestTranslatableMixin):
    """Optimization objective.

    :param goal: Defines supported metric goals for hyperparameter tuning. Accepted values
     are: "minimize", "maximize".
    :type goal: str
    :param primary_metric: The name of the metric to optimize.
    :type primary_metric: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
            :start-after: [START configure_sweep_job_bayesian_sampling_algorithm]
            :end-before: [END configure_sweep_job_bayesian_sampling_algorithm]
            :language: python
            :dedent: 8
            :caption: Assigning an objective to a SweepJob.
    """

    def __init__(self, goal: Optional[str], primary_metric: Optional[str] = None) -> None:
        """Optimization objective.

        :param goal: Defines supported metric goals for hyperparameter tuning. Acceptable values
            are: "minimize" or "maximize".
        :type goal: str
        :param primary_metric: The name of the metric to optimize.
        :type primary_metric: str
        """
        if goal is not None:
            self.goal = goal.lower()
        self.primary_metric = primary_metric

    def _to_rest_object(self) -> RestObjective:
        return RestObjective(
            goal=self.goal,
            primary_metric=self.primary_metric,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestObjective) -> Optional["Objective"]:
        if not obj:
            return None

        return cls(goal=obj.goal, primary_metric=obj.primary_metric)
