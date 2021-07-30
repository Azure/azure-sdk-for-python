# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Optional
    import msal
    from . import AuthenticationRecord
    from ._internal import AadClientBase


try:
    from contextvars import ContextVar

    _assertion_var = ContextVar("_user_assertion_context", default=None)

    def get_assertion():
        return _assertion_var.get()

    def _set_assertion(user_assertion):
        _assertion_var.set(user_assertion)


except ImportError:
    from threading import local

    _assertion_local = local()
    _assertion_local.user_assertion = None

    def get_assertion():
        return _assertion_local.user_assertion

    def _set_assertion(user_assertion):
        _assertion_local.user_assertion = user_assertion


class UserAssertion(object):
    def __init__(self, user_assertion):
        # type: (str) -> None
        """A user assertion.

        :param str user_assertion: the user assertion. Typically an access token issued to the user.
        """
        self._assertion = user_assertion
        self._async_clients = {}  # type: Dict[str, AadClientBase]
        self._client_applications = {}  # type: Dict[str, msal.ConfidentialClientApplication]
        self._record = None  # type: Optional[AuthenticationRecord]

    def __enter__(self):
        if get_assertion():
            raise ValueError("Another UserAssertion is already active for this context")
        _set_assertion(self)
        return self

    def __exit__(self, *args):
        _set_assertion(None)
