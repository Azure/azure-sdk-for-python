# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Optional

from azure.ai.ml._restclient.v2023_08_01_preview.models import (
    FeaturesetVersionBackfillResponse as RestFeaturesetVersionBackfillResponse,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._mixins import RestTranslatableMixin


@experimental
class FeatureSetBackfillMetadata(RestTranslatableMixin):
    """Feature Set Backfill Metadata

    :param job_id: The ID of the backfill job. Defaults to None.
    :type job_id: Optional[str]
    :param type: The type of the backfill job. Defaults to None.
    :type type: Optional[str]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        job_ids: Optional[list] = None,
        # pylint: disable=redefined-builtin
        type: Optional[str] = None,
        # pylint: disable=unused-argument
        **kwargs: Any
    ) -> None:
        self.type = type if type else "BackfillMaterialization"
        self.job_ids = job_ids

    @classmethod
    def _from_rest_object(cls, obj: RestFeaturesetVersionBackfillResponse) -> Optional["FeatureSetBackfillMetadata"]:
        if not obj:
            return None
        return FeatureSetBackfillMetadata(job_ids=obj.job_ids)
