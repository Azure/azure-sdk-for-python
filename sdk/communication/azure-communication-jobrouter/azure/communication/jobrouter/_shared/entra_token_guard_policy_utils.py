# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
from datetime import datetime, timezone
from dateutil import parser as dateutil_parser # type: ignore


class EntraTokenGuardUtils:
    @staticmethod
    def is_entra_token_cache_valid(entra_token_cache, request):
        current_entra_token = request.http_request.headers.get("Authorization", "")
        cache_valid = (
            entra_token_cache is not None and
            current_entra_token == entra_token_cache
        )
        return cache_valid, current_entra_token

    @staticmethod
    def is_acs_token_cache_valid(response_cache):
        if (response_cache is None or response_cache.http_response is None or
                response_cache.http_response.status_code != 200):
            return False
        try:
            content = response_cache.http_response.text()
            data = json.loads(content)
            expires_on = data["accessToken"]["expiresOn"]
            expires_on_dt = dateutil_parser.parse(expires_on)
            return datetime.now(timezone.utc) < expires_on_dt
        except (KeyError, ValueError, json.JSONDecodeError):
            return False
