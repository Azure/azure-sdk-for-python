# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    Objective as RestObjective,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class Objective(RestTranslatableMixin):
    """Optimization objective.

    All required parameters must be populated in order to send to Azure.

    :param goal: Required. Defines supported metric goals for hyperparameter tuning. Possible values
     include: "minimize", "maximize".
    :type goal: str
    :param primary_metric: Required. Name of the metric to optimize.
    :type primary_metric: str
    """

    def __init__(self, goal: Optional[str] = None, primary_metric: Optional[str] = None):
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
