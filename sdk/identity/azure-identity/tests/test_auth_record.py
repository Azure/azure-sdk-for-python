# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json

from azure.identity._auth_record import AuthenticationRecord


def test_serialization():
    """serialize should accept arbitrary additional key/value pairs, which deserialize should ignore"""

    attrs = ("authority", "client_id","home_account_id", "tenant_id", "username")
    nums = (n for n in range(len(attrs)))
    record_values = {attr: next(nums) for attr in attrs}

    record = AuthenticationRecord(**record_values)
    serialized = record.serialize()

    # AuthenticationRecord's fields should have been serialized
    assert json.loads(serialized) == record_values

    deserialized = AuthenticationRecord.deserialize(serialized)

    # the deserialized record and the constructed record should have the same fields
    assert sorted(vars(deserialized)) == sorted(vars(record))

    # the constructed and deserialized records should have the same values
    assert all(getattr(deserialized, attr) == record_values[attr] for attr in attrs)
