# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    FeaturesetVersionBackfillResponse as RestFeaturesetVersionBackfillResponse,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._utils._experimental import experimental


@experimental
class FeatureSetBackfillMetadata(RestTranslatableMixin):
    """_summary_

    :param job_id: The ID of the backfill job. Defaults to None.
    :type job_id: Optional[str]
    :param type: The type of the backfill job. Defaults to None.
    :type type: Optional[str]

    TODO: FInish this docstring
    """
    def __init__(
        self,
        *,
        job_id: Optional[str] = None,
        type: Optional[str] = None,  # pylint: disable=redefined-builtin
        **kwargs  # pylint: disable=unused-argument
    ) -> None:
        self.type = type if type else "BackfillMaterialization"
        self.job_id = job_id

    @classmethod
    def _from_rest_object(cls, obj: RestFeaturesetVersionBackfillResponse) -> "FeatureSetBackfillMetadata":
        if not obj:
            return None
        return FeatureSetBackfillMetadata(job_id=obj.job_id)
