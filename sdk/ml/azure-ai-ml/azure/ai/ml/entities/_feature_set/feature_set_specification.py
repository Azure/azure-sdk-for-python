# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._restclient.v2023_10_01.models import FeaturesetSpecification as RestFeaturesetSpecification
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class FeatureSetSpecification(RestTranslatableMixin):
    """Feature Set Specification

    :param path: Specifies the feature set spec path to file. Defaults to None.
    :type path: Optional[str]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_featurestore.py
            :start-after: [START configure_feature_set]
            :end-before: [END configure_feature_set]
            :language: python
            :dedent: 8
            :caption: Using Feature Set Spec to create Feature Set
    """

    def __init__(self, *, path: Optional[str] = None, **kwargs) -> None:  # pylint: disable=unused-argument
        self.path = path

    def _to_rest_object(self) -> RestFeaturesetSpecification:
        return RestFeaturesetSpecification(path=self.path)

    @classmethod
    def _from_rest_object(cls, obj: RestFeaturesetSpecification) -> "FeatureSetSpecification":
        if not obj:
            return None
        return FeatureSetSpecification(path=obj.path)
