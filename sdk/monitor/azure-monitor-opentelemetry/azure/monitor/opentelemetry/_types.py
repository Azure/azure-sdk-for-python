# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Sequence, Union

from opentelemetry.sdk.metrics.export import MetricReader
from opentelemetry.sdk.metrics.view import View
from opentelemetry.sdk.resources import Resource

ConfigurationValue = Union[
    str,
    bool,
    int,
    float,
    Resource,
    Sequence[str],
    Sequence[bool],
    Sequence[int],
    Sequence[float],
    Sequence[MetricReader],
    Sequence[View],
]
