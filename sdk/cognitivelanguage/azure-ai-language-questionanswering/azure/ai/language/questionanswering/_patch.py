# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import six

from .models import TextRecord


def _validate_text_records(records):
    if not records:
        raise ValueError("Input records can not be empty or None")

    if isinstance(records, six.string_types):
        raise TypeError("Input records cannot be a string.")

    if isinstance(records, dict):
        raise TypeError("Input records cannot be a dict")

    if not all(isinstance(x, six.string_types) for x in records):
        if not all(
            isinstance(x, (dict, TextRecord))
            for x in records
        ):
            raise TypeError(
                "Mixing string and dictionary/object record input unsupported."
            )

    request_batch = []
    for idx, doc in enumerate(records):
        if isinstance(doc, six.string_types):
            record = {"id": str(idx), "text": doc}
            request_batch.append(record)
        else:
            request_batch.append(doc)
    return request_batch
