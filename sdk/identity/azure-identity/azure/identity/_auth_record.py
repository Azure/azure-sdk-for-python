# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json


SUPPORTED_VERSIONS = {"1.0"}


class AuthenticationRecord(object):
    """Non-secret account information for an authenticated user

    This class enables :class:`DeviceCodeCredential` and :class:`InteractiveBrowserCredential` to access
    previously cached authentication data. Applications shouldn't construct instances of this class. They should
    instead acquire one from a credential's **authenticate** method, such as
    :func:`InteractiveBrowserCredential.authenticate`. See the user_authentication sample for more details.
    """

    def __init__(self, tenant_id, client_id, authority, home_account_id, username):
        # type: (str, str, str, str, str) -> None
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

    @classmethod
    def deserialize(cls, data):
        # type: (str) -> AuthenticationRecord
        """Deserialize a record.

        :param str data: a serialized record
        """

        deserialized = json.loads(data)

        version = deserialized.get("version")
        if version not in SUPPORTED_VERSIONS:
            raise ValueError(
                'Unexpected version "{}". This package supports these versions: {}'.format(version, SUPPORTED_VERSIONS)
            )

        return cls(
            authority=deserialized["authority"],
            client_id=deserialized["clientId"],
            home_account_id=deserialized["homeAccountId"],
            tenant_id=deserialized["tenantId"],
            username=deserialized["username"],
        )

    def serialize(self):
        # type: () -> str
        """Serialize the record.

        :rtype: str
        """

        record = {
            "authority": self._authority,
            "clientId": self._client_id,
            "homeAccountId": self._home_account_id,
            "tenantId": self._tenant_id,
            "username": self._username,
            "version": "1.0",
        }

        return json.dumps(record)
