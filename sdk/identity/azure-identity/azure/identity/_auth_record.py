# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class AuthenticationRecord(object):
    """A record which can initialize :class:`DeviceCodeCredential` or :class:`InteractiveBrowserCredential`"""

    def __init__(self, tenant_id, client_id, authority, home_account_id, username, **kwargs):
        # type: (str, str, str, str, str, **Any) -> None
        self._additional_data = kwargs
        self._authority = authority
        self._client_id = client_id
        self._home_account_id = home_account_id
        self._tenant_id = tenant_id
        self._username = username

    @property
    def authority(self):
        # type: () -> str
        return self._authority

    @property
    def client_id(self):
        # type: () -> str
        return self._client_id

    @property
    def home_account_id(self):
        # type: () -> str
        return self._home_account_id

    @property
    def tenant_id(self):
        # type: () -> str
        return self._tenant_id

    @property
    def username(self):
        # type: () -> str
        """The authenticated user's username"""
        return self._username

    @property
    def additional_data(self):
        # type: () -> dict
        """Keyword arguments serialized with the record"""

        return dict(self._additional_data)

    def __getitem__(self, key):
        return getattr(self, key, None) or self._additional_data[key]

    @classmethod
    def deserialize(cls, json_string):
        # type: (str) -> AuthenticationRecord
        """Deserialize a record from JSON"""

        deserialized = json.loads(json_string)

        return cls(
            authority=deserialized.pop("authority"),
            client_id=deserialized.pop("client_id"),
            home_account_id=deserialized.pop("home_account_id"),
            tenant_id=deserialized.pop("tenant_id"),
            username=deserialized.pop("username"),
            **deserialized
        )

    def serialize(self, **kwargs):
        # type: (**Any) -> str
        """Serialize the record and any keyword arguments to JSON"""

        record = dict(
            {
                "authority": self._authority,
                "client_id": self._client_id,
                "home_account_id": self._home_account_id,
                "tenant_id": self._tenant_id,
                "username": self._username,
            },
            **kwargs
        )

        return json.dumps(record)
