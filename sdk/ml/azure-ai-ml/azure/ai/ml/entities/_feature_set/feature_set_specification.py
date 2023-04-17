# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._restclient.v2023_02_01_preview.models import FeaturesetSpecification as RestFeaturesetSpecification
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._utils._experimental import experimental


@experimental
class FeatureSetSpecification(RestTranslatableMixin):
    def __init__(self, *, path: Optional[str] = None, **kwargs):  # pylint: disable=unused-argument
        """
        :param path: Specifies the spec path.
        :type path: str
        """
        self.path = path

    def _to_rest_object(self) -> RestFeaturesetSpecification:
        return RestFeaturesetSpecification(path=self.path)

    @classmethod
    def _from_rest_object(cls, obj: RestFeaturesetSpecification) -> "FeatureSetSpecification":
        if not obj:
            return None
        return FeatureSetSpecification(path=obj.path)
