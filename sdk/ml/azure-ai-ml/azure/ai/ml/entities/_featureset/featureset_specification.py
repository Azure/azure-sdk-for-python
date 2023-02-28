# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._restclient.v2023_02_01_preview.models import FeaturesetSpecification as RestFeaturesetSpecification
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class FeaturesetSpecification(RestTranslatableMixin):
    def __init__(
        self,
        *,
        path: Optional[str] = None,
    ):
        """
        :keyword path: Specifies the spec path.
        :paramtype path: str
        """
        self.path = path

    def _to_rest_object(self) -> RestFeaturesetSpecification:
        return RestFeaturesetSpecification(path=self.path)

    @classmethod
    def _from_rest_object(cls, obj: RestFeaturesetSpecification) -> "FeaturesetSpecification":
        if not obj:
            return None
        return FeaturesetSpecification(path=obj.path)
