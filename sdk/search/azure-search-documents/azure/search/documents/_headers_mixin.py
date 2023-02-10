# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Optional, Dict, Any


class HeadersMixin:
    @property
    def _headers(self) -> Dict[str, Any]:
        return {"api-key": self._credential.key, "Accept": self._ODATA_ACCEPT}

    def _merge_client_headers(self, headers: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if self._aad:
            return headers
        headers = headers or {}
        combined = self._headers
        combined.update(headers)
        return combined
