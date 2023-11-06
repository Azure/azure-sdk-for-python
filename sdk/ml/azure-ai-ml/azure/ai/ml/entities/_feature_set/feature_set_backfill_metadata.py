# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, List, Optional

from azure.ai.ml._restclient.v2023_10_01.models import (
    FeaturesetVersionBackfillResponse as RestFeaturesetVersionBackfillResponse,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class FeatureSetBackfillMetadata(RestTranslatableMixin):
    """Feature Set Backfill Metadata

    :param job_ids: A list of IDs of the backfill jobs. Defaults to None.
    :type job_ids: Optional[List[str]]
    :param type: The type of the backfill job. Defaults to None.
    :type type: Optional[str]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        job_ids: Optional[List[str]] = None,
        type: Optional[str] = None,  # pylint: disable=redefined-builtin
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
