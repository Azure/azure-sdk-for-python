# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, List, Optional
from .._generated import _serialization
from .._generated.models import Vector as _Vector

class SearchQueryVector(_serialization.Model):
    """The query parameters for vector and hybrid search queries.

    :ivar value: The vector representation of a search query.
    :vartype value: list[float]
    :ivar k_nearest_neighbors_count: Number of nearest neighbors to return as top hits.
    :vartype k_nearest_neighbors_count: int
    :ivar fields: Vector Fields of type Collection(Edm.Single) to be included in the vector
     searched.
    :vartype fields: str
    """

    _attribute_map = {
        "value": {"key": "value", "type": "[float]"},
        "k_nearest_neighbors_count": {"key": "kNearestNeighborsCount", "type": "int"},
        "fields": {"key": "fields", "type": "str"},
    }

    def __init__(
        self,
        *,
        value: Optional[List[float]] = None,
        k_nearest_neighbors_count: Optional[int] = None,
        fields: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword value: The vector representation of a search query.
        :paramtype value: list[float]
        :keyword k_nearest_neighbors_count: Number of nearest neighbors to return as top hits.
        :paramtype k_nearest_neighbors_count: int
        :keyword fields: Vector Fields of type Collection(Edm.Single) to be included in the vector
         searched.
        :paramtype fields: str
        """
        super().__init__(**kwargs)
        self.value = value
        self.k_nearest_neighbors_count = k_nearest_neighbors_count
        self.fields = fields


    def _to_generated(self):
        return _Vector(
            value=self.value,
            k=self.k_nearest_neighbors_count,
            fields=self.fields,
        )

    @classmethod
    def _from_generated(cls, vector):
        if not vector:
            return None
        return cls(
            value=vector.value,
            k_nearest_neighbors_count=vector.k,
            fields=vector.fields,
        )
