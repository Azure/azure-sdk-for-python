# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

from requests.structures import CaseInsensitiveDict


class CosmosResponse(dict):
    def __init__(self, original_dict, response_headers):
        super().__init__(original_dict)
        self._response_headers = response_headers

    def response_headers(self) -> CaseInsensitiveDict:
        """Returns the response headers associated to this result

        :return: Dict of response headers
        :rtype: ~requests.structures.CaseInsensitiveDict"
        """
        return self._response_headers

    def __repr__(self):
        # Custom representation to include headers in the output
        return f"{super().__repr__()} with response headers: {self._response_headers}"
