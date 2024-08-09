# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

from typing import Any, Dict, Iterable, Mapping
from azure.core.utils import CaseInsensitiveDict


class CosmosDictResponse(dict):
    def __init__(self, original_dict: Mapping[str, Any], /, *, response_headers: CaseInsensitiveDict) -> None:
        if original_dict is None:
            original_dict = {}
        super().__init__(original_dict)
        self._response_headers = response_headers

    @property
    def response_headers(self) -> CaseInsensitiveDict:
        """Returns the response headers associated to this result

        :return: Dict of response headers
        :rtype: ~azure.core.CaseInsensitiveDict
        """
        return self._response_headers


class CosmosListResponse(list):
    def __init__(self, original_list: Iterable[Dict[str, Any]], /, *,
                 response_headers: CaseInsensitiveDict) -> None:
        if original_list is None:
            original_list = []
        super().__init__(original_list)
        self._response_headers = response_headers

    @property
    def response_headers(self) -> CaseInsensitiveDict:
        """Returns the response headers associated to this result

        :return: Dict of response headers
        :rtype: ~azure.core.CaseInsensitiveDict
        """
        return self._response_headers
