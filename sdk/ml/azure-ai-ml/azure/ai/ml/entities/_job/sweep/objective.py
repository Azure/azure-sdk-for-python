# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.ml.entities._mixins import RestTranslatableMixin

from azure.ai.ml._restclient.v2022_02_01_preview.models import Objective as RestObjective
from typing import Optional
from azure.ai.ml.entities._util import SnakeToPascalDescriptor


class Objective(RestObjective):
    """Optimization objective.

    All required parameters must be populated in order to send to Azure.

    :param goal: Required. Defines supported metric goals for hyperparameter tuning. Possible values
     include: "minimize", "maximize".
    :type goal: str
    :param primary_metric: Required. Name of the metric to optimize.
    :type primary_metric: str
    """

    goal = SnakeToPascalDescriptor()

    def __init__(self, goal: str = None, primary_metric: str = None, **kwargs):
        RestObjective.__init__(self, goal=goal, primary_metric=primary_metric, **kwargs)

    @classmethod
    def _from_rest_object(cls, obj: RestObjective) -> Optional["Objective"]:
        if not obj:
            return None

        return cls(goal=obj.goal, primary_metric=obj.primary_metric)
