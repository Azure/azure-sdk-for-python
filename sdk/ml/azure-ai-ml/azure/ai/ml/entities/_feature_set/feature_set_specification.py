# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._restclient.v2023_04_01_preview.models import FeaturesetSpecification as RestFeaturesetSpecification
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._mixins import RestTranslatableMixin


@experimental
class FeatureSetSpecification(RestTranslatableMixin):
    """Feature Set Specification

    :param path: Specifies the feature set spec path. Defaults to None.
    :type path: Optional[str]    
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
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
