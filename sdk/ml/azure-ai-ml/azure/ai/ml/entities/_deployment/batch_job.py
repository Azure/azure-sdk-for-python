# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._restclient.v2020_09_01_dataplanepreview.models import BatchJobResource


class BatchJob(object):

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.name = kwargs.get("name", None)
        self.type =  kwargs.get("type", None)

    def _to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
        }

    @classmethod
    def _from_rest_object(cls, obj: BatchJobResource) -> "BatchJob":
        return cls(
            id=obj.id,
            name=obj.name,
            type=obj.type,
        )
