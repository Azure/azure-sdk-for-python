# The MIT License (MIT)
# Copyright (c) 2023 Microsoft Corporation

from typing import Any, Mapping, Optional
from . import http_constants


class CosmosItem(dict):
    response_headers: Mapping[str, Any]

    @property
    def etag(self) -> Optional[str]:
        return self.response_headers.get(http_constants.HttpHeaders.ETag)

    @property
    def session_token(self):
        return self.response_headers.get(http_constants.HttpHeaders.SessionToken)
