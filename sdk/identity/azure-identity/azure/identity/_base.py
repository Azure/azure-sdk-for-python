# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Optional, Union


class ClientSecretCredentialBase(object):
    """Sans I/O base for client secret credentials"""

    def __init__(self, tenant_id, client_id, secret, **kwargs):  # pylint:disable=unused-argument
        # type: (str, str, str, **Any) -> None
        if not client_id:
            raise ValueError("client_id should be the id of an Azure Active Directory application")
        if not secret:
            raise ValueError("secret should be an Azure Active Directory application's client secret")
        if not tenant_id:
            raise ValueError(
                "tenant_id should be an Azure Active Directory tenant's id (also called its 'directory id')"
            )
        self._form_data = {"client_id": client_id, "client_secret": secret, "grant_type": "client_credentials"}
        super(ClientSecretCredentialBase, self).__init__()
