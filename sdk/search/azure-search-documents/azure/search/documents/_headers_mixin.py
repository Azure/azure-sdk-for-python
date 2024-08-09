# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Optional, Dict, Any, MutableMapping


class HeadersMixin:
    @property
    def _headers(self) -> Dict[str, Any]:
        if self._aad:  # type: ignore
            return {"Accept": self._ODATA_ACCEPT}  # type: ignore
        return {"api-key": self._credential.key, "Accept": self._ODATA_ACCEPT}  # type: ignore

    def _merge_client_headers(self, headers: Optional[MutableMapping[str, str]]) -> MutableMapping[str, str]:
        headers = headers or {}
        combined = self._headers
        combined.update(headers)
        return combined
