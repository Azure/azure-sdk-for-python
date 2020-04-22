# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json

from azure.identity import AuthenticationRecord


def test_serialization():
    """serialize should accept arbitrary additional key/value pairs, which deserialize should ignore"""

    attrs = ("authority", "client_id","home_account_id", "tenant_id", "username")
    nums = (n for n in range(len(attrs)))
    record_values = {attr: next(nums) for attr in attrs}
    additional_data = {"foo": "bar", "bar": "foo"}

    record = AuthenticationRecord(**record_values)
    serialized = record.serialize(**additional_data)

    # AuthenticationRecord's fields and the additional data should have been serialized
    assert json.loads(serialized) == dict(record_values, **additional_data)

    deserialized = AuthenticationRecord.deserialize(serialized)

    # the deserialized record and the constructed record should have the same fields
    assert sorted(vars(deserialized)) == sorted(vars(record))

    # the constructed and deserialized records should have the same values
    assert all(getattr(deserialized, attr) == record_values[attr] for attr in attrs)

    # deserialized record should expose additional data like a dictionary
    assert all(deserialized[key] == additional_data[key] for key in additional_data)
