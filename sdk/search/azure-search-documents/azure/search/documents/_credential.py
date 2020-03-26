# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional


class HeadersMixin(object):
    @property
    def _headers(self):
        # type() -> dict
        return {"api-key": self._credential.key, "Accept": self._ODATA_ACCEPT}

    def _merge_client_headers(self, headers):
        # type(Optional[dict]) -> dict
        headers = headers or {}
        combined = self._headers
        combined.update(headers)
        return combined
