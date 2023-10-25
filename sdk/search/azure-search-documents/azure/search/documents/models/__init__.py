# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
from typing import Optional, List, Any
from .._generated.models import (
    AnswerResult,
    AutocompleteMode,
    CaptionResult,
    IndexAction,
    IndexingResult,
    QueryAnswerType,
    QueryCaptionType,
    QueryType,
    ScoringStatistics,
    SearchMode,
    SemanticErrorMode,
    VectorFilterMode,
    VectorizableQuery,
    VectorQuery as _VectorQuery,
)


class VectorQuery(VectorizableQuery):
    """The query parameters to use for vector search when a raw vector value is provided.

    All required parameters must be populated in order to send to Azure.

    :ivar kind: The kind of vector query being performed. Required. "vector"
    :vartype kind: str or ~search_index_client.models.VectorQueryKind
    :ivar k_nearest_neighbors: Number of nearest neighbors to return as top hits.
    :vartype k_nearest_neighbors: int
    :ivar fields: Vector Fields of type Collection(Edm.Single) to be included in the vector
     searched.
    :vartype fields: str
    :ivar exhaustive: When true, triggers an exhaustive k-nearest neighbor search across all
     vectors within the vector index. Useful for scenarios where exact matches are critical, such as
     determining ground truth values.
    :vartype exhaustive: bool
    :ivar vector: The vector representation of a search query.
    :vartype vector: list[float]
    """

    _validation = {
        "kind": {"required": True},
    }

    _attribute_map = {
        "kind": {"key": "kind", "type": "str"},
        "k_nearest_neighbors": {"key": "kNearestNeighbors", "type": "int"},
        "fields": {"key": "fields", "type": "str"},
        "exhaustive": {"key": "exhaustive", "type": "bool"},
        "vector": {"key": "vector", "type": "[float]"},
    }

    def __init__(
        self,
        *,
        k_nearest_neighbors: Optional[int] = None,
        fields: Optional[str] = None,
        exhaustive: Optional[bool] = None,
        vector: Optional[List[float]] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword k_nearest_neighbors: Number of nearest neighbors to return as top hits.
        :paramtype k_nearest_neighbors: int
        :keyword fields: Vector Fields of type Collection(Edm.Single) to be included in the vector
         searched.
        :paramtype fields: str
        :keyword exhaustive: When true, triggers an exhaustive k-nearest neighbor search across all
         vectors within the vector index. Useful for scenarios where exact matches are critical, such as
         determining ground truth values.
        :paramtype exhaustive: bool
        :keyword vector: The vector representation of a search query.
        :paramtype vector: list[float]
        """
        super().__init__(k_nearest_neighbors=k_nearest_neighbors, fields=fields, exhaustive=exhaustive, **kwargs)
        self.kind: str = "vector"
        self.vector = vector

    def _to_generated(self) -> _VectorQuery:
        return _VectorQuery(
            k=self.k_nearest_neighbors,
            fields=self.fields,
            exhaustive=self.exhaustive,
            vector=self.vector,
        )


__all__ = (
    "AnswerResult",
    "AutocompleteMode",
    "CaptionResult",
    "IndexAction",
    "IndexingResult",
    "QueryAnswerType",
    "QueryCaptionType",
    "QueryType",
    "VectorQuery",
    "ScoringStatistics",
    "SearchMode",
    "SemanticErrorMode",
    "VectorFilterMode",
    "VectorizableQuery",
)
