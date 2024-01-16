# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,no-member

from typing import Any, Optional

from azure.ai.ml._restclient.v2023_04_01_preview.models import StackEnsembleSettings as RestStackEnsembleSettings
from azure.ai.ml._restclient.v2023_04_01_preview.models import StackMetaLearnerType
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class StackEnsembleSettings(RestTranslatableMixin):
    """Advance setting to customize StackEnsemble run."""

    def __init__(
        self,
        *,
        stack_meta_learner_k_wargs: Optional[Any] = None,
        stack_meta_learner_train_percentage: float = 0.2,
        stack_meta_learner_type: Optional[StackMetaLearnerType] = None,
        **kwargs: Any
    ):
        """
        :param stack_meta_learner_k_wargs: Optional parameters to pass to the initializer of the
         meta-learner.
        :type stack_meta_learner_k_wargs: any
        :param stack_meta_learner_train_percentage: Specifies the proportion of the training set
         (when choosing train and validation type of training) to be reserved for training the
         meta-learner. Default value is 0.2.
        :type stack_meta_learner_train_percentage: float
        :param stack_meta_learner_type: The meta-learner is a model trained on the output of the
         individual heterogeneous models. Possible values include: "None", "LogisticRegression",
         "LogisticRegressionCV", "LightGBMClassifier", "ElasticNet", "ElasticNetCV",
         "LightGBMRegressor", "LinearRegression".
        :type stack_meta_learner_type: str or
         ~azure.mgmt.machinelearningservices.models.StackMetaLearnerType
        """
        super(StackEnsembleSettings, self).__init__(**kwargs)
        self.stack_meta_learner_k_wargs = stack_meta_learner_k_wargs
        self.stack_meta_learner_train_percentage = stack_meta_learner_train_percentage
        self.stack_meta_learner_type = stack_meta_learner_type

    def _to_rest_object(self) -> RestStackEnsembleSettings:
        return RestStackEnsembleSettings(
            stack_meta_learner_k_wargs=self.stack_meta_learner_k_wargs,
            stack_meta_learner_train_percentage=self.stack_meta_learner_train_percentage,
            stack_meta_learner_type=self.stack_meta_learner_type,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestStackEnsembleSettings) -> "StackEnsembleSettings":
        return cls(
            stack_meta_learner_k_wargs=obj.stack_meta_learner_k_wargs,
            stack_meta_learner_train_percentage=obj.stack_meta_learner_train_percentage,
            stack_meta_learner_type=obj.stack_meta_learner_type,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StackEnsembleSettings):
            return NotImplemented

        return (
            super().__eq__(other)
            and self.stack_meta_learner_k_wargs == other.stack_meta_learner_k_wargs
            and self.stack_meta_learner_train_percentage == other.stack_meta_learner_train_percentage
            and self.stack_meta_learner_type == other.stack_meta_learner_type
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
