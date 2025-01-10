# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------


def encode_str(data, encoding="utf-8"):
    try:
        return data.encode(encoding)
    except AttributeError:
        return data


def normalized_data_body(data, **kwargs):
    # A helper method to normalize input into AMQP Data Body format
    encoding = kwargs.get("encoding", "utf-8")
    if isinstance(data, list):
        return [encode_str(item, encoding) for item in data]
    return [encode_str(data, encoding)]
