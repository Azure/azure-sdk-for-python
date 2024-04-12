# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import PathLike
from typing import Any, Optional, Union

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

    def __init__(
        self, *, path: Optional[Union[PathLike, str]] = None, **kwargs: Any
    ):  # pylint: disable=unused-argument
        """
        :param path: Specifies the spec path.
        :type path: str
        """
        self.path = path

    def _to_rest_object(self) -> RestFeaturesetSpecification:
        return RestFeaturesetSpecification(path=self.path)

    @classmethod
    def _from_rest_object(cls, obj: RestFeaturesetSpecification) -> Optional["FeatureSetSpecification"]:
        if not obj:
            return None
        return FeatureSetSpecification(path=obj.path)
