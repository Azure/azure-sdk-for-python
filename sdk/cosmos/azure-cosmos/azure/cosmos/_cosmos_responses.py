# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

from azure.core.utils import CaseInsensitiveDict


class CosmosDictResponse(dict):
    def __init__(self, original_dict, response_headers):
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
    def __init__(self, original_list, response_headers):
        super().__init__(original_list)
        self._response_headers = response_headers

    @property
    def response_headers(self) -> CaseInsensitiveDict:
        """Returns the response headers associated to this result

        :return: Dict of response headers
        :rtype: ~azure.core.CaseInsensitiveDict
        """
        return self._response_headers
